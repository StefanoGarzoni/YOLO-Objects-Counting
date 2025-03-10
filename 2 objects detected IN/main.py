#MAIN DEL PROGRAMMA
import sys
from PyQt5.QtWidgets import QWidget, QApplication,QMessageBox
from countingYoloRT10Pollici import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import time
from pathlib import Path
import cv2
from ultralytics import YOLO
import supervision as sv
from line_zoneLib import LineZoneNew
import pymssql
import logging
from datetime import datetime
import subprocess   
import os


day= datetime.today().date()
fileLog='filesLog/'+str(day)+'.log'

LINE_START = sv.Point(200, 0)
LINE_END = sv.Point(200, 480)

logging.basicConfig(filename=fileLog, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#thread containing the for loop
class Worker(QObject):   
    #creating variables
    logging.info('Creating worker class')
    space = [0,0,1,0,0,0,0,0]
    go = False
    last = 0
    total = 0
    x = 0
    nLav = 1
    line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
    model = None
    start=True
    modello = ""
    nCic=0
    i=0
    crN=[]
    crC=[]
    ganci=0
    telai=0
    er=0
    lastT=0
    lastG=0

    server = "dbIP"
    database = "dbName"
    username = "username"
    password = "password"
    query = "UPDATE tblCounting SET obj1 = %d, Obj2 = %s WHERE idRow = 1" 
    queryRead= "SELECT * FROM tblCtrl"
    queryError="INSERT INTO tblLogErrors (Error, DateTime) VALUES (%s, %s)"
    
    logging.info('Connecting pulses')
    #creating thread pulses
    txtObjTotEdit = pyqtSignal(str) #pulse to modify the total text field
    txtObjInEdit = pyqtSignal(str)  #pulse to modify the counted objects text field
    txtObjOutEdit = pyqtSignal(str) #pulse to modify the outgoing objects text field
    txtLavEdit = pyqtSignal(str)    #pulse to modify the work change text field
    pixmapSet = pyqtSignal(QPixmap) #pulse to send video frames to the label
    startLav = pyqtSignal() #pulse to mark the start of work
    
    
    #function containing the FOR loop for Object detection
    def run(self):

        global day
        global fileLog

        logging.info('Starting run method')

        self.go = True #start the work
        self.line_counter = LineZoneNew(start=LINE_START, end=LINE_END)
        line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=1, text_scale=0.5)
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )

        logging.info('Retrieving data from obj1.txt and obj2.txt files')
        if self.er==0:
            self.er=1
            try:
                with open("utilityFiles/obj2.txt", 'r') as file:
                    content = file.read()
                self.line_counter.in_count=int(content)
                self.telai=int(content)
                self.total=int(content)
                self.lastT=self.total
                with open("utilityFiles/obj1.txt", 'r') as file:
                    content = file.read()
                self.ganci=int(content)
                self.lastG=self.ganci
            except Exception as e:
                logging.warning("Error reading files - Note that the frame and hook count starts from 0\n - error: %s",e)


        logging.info('Starting main for loop')
        try:
            for result in self.model.track(source=0, stream=True, agnostic_nms=True, device=0, conf=0.6):
                logging.info('Cycle n: %d',self.i)
                if self.start == True:
                    self.startLav.emit()
                    self.start = False
                

                if self.go == True:
                    frame = result.orig_img
                    detections = sv.Detections.from_yolov8(result)
                    
                    if result.boxes.id is not None:
                        detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
                    
                    
                    labels = [
                        f"{tracker_id} {self.model.model.names[class_id]} {confidence:0.2f}"
                        for _, confidence, class_id, tracker_id
                        in detections
                    ]
                    
                    frame = box_annotator.annotate(
                        scene=frame, 
                        detections=detections,
                        labels=labels
                    )
                    
                    ris=self.line_counter.trigger(detections=detections)
                    line_annotator.annotate(frame=frame, line_counter=self.line_counter)

                    
                    #adapting frame image to QImage for display
                    height, width, bytesPerComponent = frame.shape
                    bytesPerLine = bytesPerComponent * width
                    
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    image = QImage(frame_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)
                    
                    for id in 5:
                        if id==-1:
                            continue
                        if id==1: #id frame=1 id bottle=39
                            self.telai+=1
                            logging.info('Incrementing frame counter: (%d)',self.telai)
                        else :
                            if id==0: #id hook=0 id phone=67
                                self.ganci+=1
                                logging.info('Incrementing hook counter: (%d)',self.ganci)

                    if self.lastT!= self.telai or self.lastG!=self.ganci:
                        logging.info('Changing value of hooks and frames variables -> writing to files')
                        #writing to file
                        self.write_to_file_gt("utilityFiles/obj1.txt", f'{self.ganci}')
                        self.write_to_file_gt("utilityFiles/obj2.txt", f'{self.telai}')

                        #query
                        conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                        cursor = conn.cursor()
                        logging.info('Updating the database')
                        try:
                            cursor.execute(self.query,(self.ganci, str(self.telai)))
                            conn.commit()
                            

                        except Exception as e:
                            logging.error('Error executing query: %s',e)
                            print(f"Error executing query: {e}")
                            conn.rollback()

                        finally:
                            conn.close()

                    self.lastT=self.telai
                    self.lastG=self.ganci
                    self.total=self.telai
                    
                    logging.info('Emitting data update pulses - file and graphical interface')
                    #pulses emitted by the Thread
                    self.pixmapSet.emit(QPixmap.fromImage(image))
                    self.txtObjTotEdit.emit(str(self.total))
                    self.txtObjInEdit.emit(str(self.telai))
                    self.txtObjOutEdit.emit(str(self.ganci))
                    self.txtLavEdit.emit(str(self.nLav))
                    
                    if(self.i%700==0 and self.i!=0):
                        try:
                            logging.info('Reading the file containing the temperature')
                            try:
                                with open("/sys/devices/virtual/thermal/thermal_zone0/temp") as temp_file:
                                    temp = temp_file.read().strip()
                                    temp_celsius = float(temp) / 1000.0 #conversion
                                logging.info("Recorded temperature: %s",temp_celsius)
                            except Exception as e:
                                temp_celsius=0.0
                                logging.error("Error retrieving CPU temperature from file:", e)

                            if(temp_celsius>=55 and temp_celsius<70):
                                logging.info('Temperature above 55 degrees')
                                
                            elif temp_celsius>=70 and temp_celsius <78:
                                logging.info('Temperature above 70 degrees')
                                
                            elif temp_celsius>=78 and temp_celsius <85:
                                logging.info('Temperature above 78 degrees')
                               
                            elif temp_celsius>=85:
                                logging.error('Temperature above 85 degrees -> stopping the for loop')
                                try:
                                    conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                                    cursor = conn.cursor()
                                    n = datetime.now()
                                    stringa_data_ora = n.strftime("%Y-%m-%d %H:%M:%S")
                                    cursor.execute(self.queryError,( 'Temperature above 85 degrees -> stopping the for loop', str(stringa_data_ora)))
                                    conn.commit()
                                    logging.warning("Error reported in the database")
                                except Exception as er:
                                    logging.error('Error connecting to the database: %s',er)
                                finally:
                                    conn.close()
                                    ctrlTemp=True
                                    while ctrlTemp:
                                        self.pixmapSet.emit("Error: waiting for adequate temperature\nContact a technician") #test updating video label
                                        time.sleep(60)
                                        logging.warning('Reading the file containing the temperature while waiting for it to be below 80 degrees')
                                        try:
                                            with open("/sys/devices/virtual/thermal/thermal_zone0/temp") as temp_file:
                                                temp = temp_file.read().strip()
                                                temp_celsius = float(temp) / 1000.0 #conversion
                                            if temp_celsius < 70:
                                                logging.warning("Temperature lowered: %s", temp_celsius)
                                                ctrlTemp=False
                                            else:
                                                logging.warning("Retrying in 1m | Temperature NOT low enough: %s", temp_celsius)
                                        except Exception as e: 
                                            logging.error("Error reading temperature file %s",e)


                            else:
                                logging.info('Temperature below 55 degrees')
                                

                        except Exception as e:
                            logging.critical('Error reading temperature: %s', e)

                        try:
                            logging.info('Checking the tblCtrl table (in the for loop)')
                            conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                            cursor = conn.cursor()
                        
                            cursor.execute(self.queryRead)
                            row = cursor.fetchone()
                            value = row[1]
                            
                            if value==0:
                                logging.info('value = 0 -> restarting the program and waiting for value = 1')
                                conn.close()
                                script_bash = "utilityFiles/reboot.sh"
                                subprocess.run(["bash", script_bash])
                            else:
                                logging.info('value = 1 -> continuing program execution')
                                
                        except Exception as e:
                            logging.error('Error executing query: %s',e)
                            print(f"Error executing query: {e}")
                            conn.rollback()
                        finally:
                            conn.close()
                    self.i+=1

                if day !=  datetime.today().date():
                    day=datetime.today().date()
                    fileLog='filesLog/'+str(day)+'.log'
                    logging.info('END OF DAY - CHANGING THE .LOG FILE')
                    logging.shutdown() 
                    os.rename(fileLog, 'filesLog/'+str(day)+'.log')  
                    logging.basicConfig(filename='filesLog/'+str(day)+'.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                    logging.info('NEW DAY - STARTING NEW .LOG FILE')  

        except Exception as e:
            logging.critical('ERROR GENERATED IN MAIN FOR LOOP: %s',e)
            try:
                conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                cursor = conn.cursor()
                n = datetime.now()
                stringa_data_ora = n.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(self.queryError,( str(e), str(stringa_data_ora)))
                conn.commit()
                logging.warning("Error reported in the database")
            except Exception as er:
                logging.error('Error connecting to the database: %s',er)
            finally:
                conn.close()

            logging.warning("RESTARTING PROGRAM - ATTEMPTING TO RESOLVE THE ERROR")
            script_bash = "utilityFiles/reboot.sh"
            subprocess.run(["bash", script_bash])
            #sys.exit(0)
                
    def setGo(self, b):
        self.go = b
    
    def write_to_file_gt(self, file_path: str, line: str) -> None:
        with open(file_path, "w") as file:
            file.write(line)

    def createProgram(self, cr):
        print((cr))
    
    def setModel(self, mod):
        logging.info("Setting the model - creating YOLO model object - model: %s",mod)
        self.modello = mod
        self.model = YOLO(self.modello)
        
        

#class for controlling the graphical interface
class Finestra(QtWidgets.QMainWindow):
    logging.info('Creating Finestra class - worker object - thread')
    work = Worker()
    thread = QThread()
    font = ""
    cont = True #used only to receive a value (not used in this program) from startRead
    ctrlStart=True
    
    #constructor of the class object
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupMainWindow(self)
        
        self.showFullScreen()
        self.work.crN=self.ui.createrValueN
        self.work.crC=self.ui.createrValueC

        global day
        global fileLog
        
        #connecting events to buttons and widgets
        self.ui.btnStart.clicked.connect(self.clickStart)
        self.ui.btnStop.clicked.connect(self.clickStop)
        self.ui.btnRestart.clicked.connect(self.clickRestart)
        self.ui.actionMenu.triggered.connect(self.changeWinMenu)
        self.ui.actionSave.triggered.connect(self.saveTot)

        self.ui.groupBoxMenu.setHidden(True) #hides the menu window
        self.ui.actionSave.setEnabled(False) #disables save action
        self.ui.groupBoxMenu.setEnabled(False)  #disables the menu window

        
        self.work.moveToThread(self.thread) #moves the Work class to a thread
          
        modelloScelto="modelli_in_uso/1v86008.pt"
        self.work.setModel(modelloScelto)
            
        logging.info('Connecting the run function to the thread')
        self.thread.started.connect(self.work.run)  #connects the thread to the function to run
        
        logging.info('Connecting pulses to functions')
        #connect pulses to their functions
        self.work.txtObjInEdit.connect(self.update_line_in)
        self.work.txtObjOutEdit.connect(self.update_line_out)
        self.work.txtLavEdit.connect(self.update_line_lav)
        self.work.pixmapSet.connect(self.update_pixmap)
        self.work.txtObjTotEdit.connect(self.update_tot) #continues to write status running
        self.work.startLav.connect(self.update_lab) 
        
        logging.info('Setting fonts and graphical interface')
        #setting fonts for widgets
        self.font = self.ui.txtOb.font()
        self.font.setPointSize(24)
        self.ui.txtObjIn.setFont(self.font)
        self.ui.txtObjOut.setFont(self.font)
        self.ui.txtOb.setFont(self.font)
        self.ui.txtLav.setFont(self.font)
        self.ui.txtObjTot.setFont(self.font)
        
        #setting fonts for radio buttons
        font1 = QFont()
        font1.setPointSize(30)
        for valori in self.ui.radioButtons.values() :   
            for valore in valori:
                valore.setFont(font1)
        
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #48c75b;}")
        self.ui.btnStop.setStyleSheet("#btnStop{background-color: #a3a8a5;}")
        self.ui.btnRestart.setStyleSheet("#btnRestart{background-color: #a3a8a5;}")
        

        #loading text of the program while waiting for the webcam connection
        self.ui.label.setText("Waiting...")#Loading
        custom_font = QFont()
        custom_font.setPointSize(20)
        self.ui.label.setFont(custom_font)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        
        logging.info('First check of the tblCtrl table')
        log=0
        while self.ctrlStart:
                
                conn = pymssql.connect(server=self.work.server, user=self.work.username, password=self.work.password, database=self.work.database)
                cursor = conn.cursor()
                try:
                    cursor.execute(self.work.queryRead)
                    row = cursor.fetchone()
                    value = row[1]
                    
                    if value==1:
                        logging.info('value = 1 - ending the while loop - starting the thread with go bit set to True')
                        self.ctrlStart=False
                        self.thread.start() #start the thread
                        self.work.go = True #start the work
        
                except Exception as e:
                    logging.error('Error executing query: %s',e)
                    print(f"Error executing query: {e}")
                    conn.rollback()

                finally:
                    conn.close()
                
                if self.ctrlStart==True:
                    if log%20==0:
                        if day !=  datetime.today().date():
                            day=datetime.today().date()
                            fileLog='filesLog/'+str(day)+'.log'
                            logging.info('END OF DAY - CHANGING THE .LOG FILE')
                            logging.shutdown() 
                            os.rename(fileLog, 'filesLog/'+str(day)+'.log')  
                            logging.basicConfig(filename='filesLog/'+str(day)+'.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                            logging.info('NEW DAY - STARTING NEW .LOG FILE')  
                    logging.info('value = 0 - Rechecking in 30 seconds...')
                    print("Value = 0 - Rechecking in 30 seconds...")
                    time.sleep(30)
                    log+=1



    #function that handles the start button  
    def clickStart(self):
        perche="removed for frame program"
       
    #function that handles the stop button
    def clickStop(self):
        perche="removed for frame program"
        
    #function that handles the restart button  
    def clickRestart(self):
        perche="removed for frame program"
    
    #save the total
    def saveTot(self):
        perche="removed for frame program"
            
    #function for switching from view to menu
    def changeWinMenu(self):
        if self.ui.groupBoxView.isHidden() == False:    #if the menu is hidden
            self.ui.groupBoxView.setHidden(True)
            self.ui.groupBoxMenu.setHidden(False)
            self.ui.actionMenu.setText("View")
        else:   
            self.ui.groupBoxView.setHidden(False)
            self.ui.groupBoxMenu.setHidden(True)
            self.ui.actionMenu.setText("Menu")
    

    def update_line_in(self, text):
        self.ui.txtObjIn.setText("Number of Frames: " + text)
        self.ui.txtObjIn.setFont(self.font)
        
    def update_tot(self, text):
        self.ui.txtObjTot.setText("Status: Running")
        self.ui.txtObjTot.setFont(self.font)
    
    def update_line_out(self, text):
        self.ui.txtObjOut.setText("Number of Hooks: " + text)
        self.ui.txtObjOut.setFont(self.font)
    
    def update_line_lav(self, text):
        self.ui.txtLav.setText("Work number: " + text)
        self.ui.txtLav.setFont(self.font)
        
    def update_pixmap(self, image):
        self.ui.label.setText("")
        self.ui.label.setPixmap(image)

    def update_lab(self):
        self.ui.label.setText("Press Start to begin\nor\nchoose options in the Menu")
        custom_font = QFont()
        custom_font.setPointSize(20)
        self.ui.label.setFont(custom_font)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.groupBoxMenu.setEnabled(False) #CHANGED FOR FRAME PROGRAM
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #48c75b;} ")##btnStart:hover{background-color: #ffffff;}
    
    
#main call
if __name__ == '__main__':

    app = QApplication(sys.argv)    #creating graphical application
    time.sleep(1)   #waiting for the graphical app to be created

    app.setStyleSheet(Path('style.qss').read_text())    #calling the qss file (python css)
    window = Finestra() #creating the window object
    
    sys.exit(app.exec())    #command to run the application
