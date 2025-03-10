#MAIN PROGRAM WITH OUT COUNTING
import sys
from PyQt5.QtWidgets import QWidget, QApplication,QMessageBox
from countingYoloRT10PolliciOUT import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import time
from pathlib import Path
import cv2
from ultralytics import YOLO
import supervision as sv
from line_zoneOUT import LineZoneNew #file with out count: line_zoneOUT.py
import pymssql
import logging
from datetime import datetime
import subprocess   
import os



day= datetime.today().date()
fileLog='filesLog/'+str(day)+'.log'

LINE_START = sv.Point(200, 0) #720, 0   |320, 0
LINE_END = sv.Point(200, 480)#720, 1000  |320, 480

logging.basicConfig(filename=fileLog, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#thread containing the for loop
class Worker(QObject):   
    #variable creation
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
    obj1=0
    obj2=0
    obj1Out=0
    obj2Out=0
    er=0
    lastT=0
    lastG=0
    lastTo=0
    lastGo=0

    server = "dbIP"
    database = "dbName"
    username = "username"
    password = "password"
    queryOut="UPDATE tblCountingOut SET obj1 = %d, obj2 = %s, obj1Out= %s, obj2Out= %s WHERE idRow = 1" #query for OUT update
    query = "UPDATE tblCounting SET obj1 = %d, Obj2 = %s WHERE idRow = 1" 
    queryRead= "SELECT * FROM tblCtrl"
    queryError="INSERT INTO tblLogErrors (Error, DateTime) VALUES (%s, %s)"
    
    logging.info('Connecting pulses')
    #creation of thread signals
    txtObjTotEdit = pyqtSignal(str) #signal to modify the total text field
    txtObjInEdit = pyqtSignal(str)  #signal to modify the counted objects text field
    txtObjOutEdit = pyqtSignal(str) #signal to modify the outgoing objects text field 
    txtLavEdit = pyqtSignal(str)    #signal to modify the work change text field
    pixmapSet = pyqtSignal(QPixmap) #signal to send video frames to the label
    startLav = pyqtSignal() #signal to mark the start of processing
    obj2OutEdit = pyqtSignal(str)
    
    
    #function containing the Object detection FOR loop
    def run(self):

        global day
        global fileLog

        logging.info('starting run method')

        self.go = True #start processing
        self.line_counter = LineZoneNew(start=LINE_START, end=LINE_END)
        line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=1, text_scale=0.5)
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )

        logging.info('retrieving data from obj1.txt and obj2.txt files')
        if self.er==0:
            self.er=1
            try:
                with open("utilityFiles/obj1.txt", 'r') as file:
                    content = file.read()
                self.line_counter.in_count=int(content)
                self.obj2=int(content)
                self.total=int(content)
                self.lastT=self.total

                with open("utilityFiles/obj2.txt", 'r') as file:
                    content = file.read()
                self.obj1=int(content)
                self.lastG=self.obj1

                with open("utilityFiles/obj1Out.txt", 'r') as file:
                    content = file.read()
                self.obj1Out=int(content)
                self.lastGo=self.obj1Out

                with open("utilityFiles/obj2Out.txt", 'r') as file:
                    content = file.read()
                self.obj2Out=int(content)
                self.lastTo=self.obj2Out
                self.line_counter.out_count=(self.lastTo+self.lastGo)

            except Exception as e:
                logging.warning("Error reading files - Warning obj2 and obj1 count starts from 0\n - error: %s",e)


        logging.info('starting main for loop')
        try:

            for result in self.model.track(source=0, stream=True, agnostic_nms=True, device=0, conf=0.5):

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
                    
                    ris, ris_out =self.line_counter.trigger(detections=detections)
                    line_annotator.annotate(frame=frame, line_counter=self.line_counter)

                    
                    #adapting frame image to QImage to display it
                    height, width, bytesPerComponent = frame.shape
                    bytesPerLine = bytesPerComponent * width
                    
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    image = QImage(frame_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)
                    
                    for id in ris:
                        if id==-1:
                            continue
                        if id==1: #id frame=1 id bottle=39
                            self.obj2+=1
                            logging.info('incrementing obj1 counter : (%d)',self.obj2)
                        else :
                            if id==0: #id hook=0 id phone=67
                                self.obj1+=1
                                logging.info('incrementing obj2 counter : (%d)',self.obj1)

                    for id1 in ris_out:
                        if id1==-1:
                            continue
                        if id1==1: #id frame=1 id bottle=39
                            self.obj2Out+=1
                            logging.info('number of obj1 out : (%d)',self.obj2Out)
                        else :
                            if id1==0: #id hook=0 id phone=67
                                self.obj1Out+=1
                                logging.info('number of obj2 out : (%d)',self.obj1Out)
                    ctrlValue=0
                    if self.lastT!= self.obj2 or self.lastG!=self.obj1:
                        logging.info('changing value of obj1 and obj2 variables -> writing to files')
                        #writing to file
                        self.write_to_file_gt("utilityFiles/obj1.txt", f'{self.obj1}')
                        self.write_to_file_gt("utilityFiles/obj2.txt", f'{self.obj2}')
                        ctrlValue=1
                    
                    if self.lastTo!= self.obj2Out or self.lastGo!=self.obj1Out:
                        logging.info('changing value of obj1 and obj2 OUT variables -> writing to files')
                        self.write_to_file_gt("utilityFiles/obj1Out.txt", f'{self.obj1Out}')
                        self.write_to_file_gt("utilityFiles/obj2Out.txt", f'{self.obj2Out}')
                        ctrlValue=1

                    if(ctrlValue==1):
                        #query
                        conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                        cursor = conn.cursor()
                        
                        try:
                            logging.info('updating the database')
                            cursor.execute(self.queryOut,(str(self.obj1), str(self.obj2), str(self.obj1Out), str(self.obj2Out)))
                            conn.commit()
                            

                        except Exception as e:
                            logging.error('Error during query execution: %s',e)
                            print(f"Error during query execution: {e}")
                            conn.rollback()

                        finally:
                            conn.close()

                    self.lastT=self.obj2
                    self.lastG=self.obj1
                    self.total=self.obj2
                    self.lastTo=self.obj2Out
                    self.lastGo=self.obj1Out
                    
                    logging.info('emitting data update signals - file and GUI')
                    #signals emitted by the Thread
                    self.pixmapSet.emit(QPixmap.fromImage(image))
                    self.txtObjTotEdit.emit(str(self.total))
                    self.txtObjInEdit.emit(str(self.obj2))
                    self.txtObjOutEdit.emit(str(self.obj1))
                    self.txtLavEdit.emit(str(self.obj1Out)) #obj2 out signal
                    self.obj2OutEdit.emit(str(self.obj2Out)) #obj1 out signal

                    if(self.i%700==0 and self.i!=0):
                        try:
                            logging.info('Reading the file containing the temperature')
                            try:
                                with open("/sys/devices/virtual/thermal/thermal_zone0/temp") as temp_file:
                                    temp = temp_file.read().strip()
                                    temp_celsius = float(temp) / 1000.0 #conversion
                                logging.info("recorded temperature: %s",temp_celsius)
                            except Exception as e:
                                temp_celsius=0.0
                                logging.error("Error retrieving CPU temperature from file :", e)

                            if(temp_celsius>=55 and temp_celsius<70):
                                logging.info('temperature over 55 degrees')
                                
                            elif temp_celsius>=70 and temp_celsius <78:
                                logging.info('temperature over 70 degrees')
                                
                            elif temp_celsius>=78 and temp_celsius <85:
                                logging.info('temperature over 78 degrees')
                               
                            elif temp_celsius>=85:
                                logging.error('temperature over 85 degrees -> stopping for loop')
                                try:
                                    conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                                    cursor = conn.cursor()
                                    n = datetime.now()
                                    stringa_data_ora = n.strftime("%Y-%m-%d %H:%M:%S")
                                    cursor.execute(self.queryError,( 'temperature over 85 degrees -> stopping for loop', str(stringa_data_ora)))
                                    conn.commit()
                                    logging.warning("Error reported on database")
                                except Exception as er:
                                    logging.error('Error connecting to database: %s',er)
                                finally:
                                    conn.close()
                                    ctrlTemp=True
                                    while ctrlTemp:
                                        self.pixmapSet.emit("error : waiting for adequate temperature\nContact a technician") #test updating video label
                                        time.sleep(60)
                                        logging.warning('Reading the file containing the temperature waiting for it to be below 80 degrees')
                                        try:
                                            with open("/sys/devices/virtual/thermal/thermal_zone0/temp") as temp_file:
                                                temp = temp_file.read().strip()
                                                temp_celsius = float(temp) / 1000.0 #conversion
                                            if temp_celsius < 70:
                                                logging.warning("lowered temperature : %s", temp_celsius)
                                                ctrlTemp=False
                                            else:
                                                logging.warning("retrying in 1m | temperature NOT low enough : %s", temp_celsius)
                                        except Exception as e: 
                                            logging.error("error reading temperature file %s",e)


                            else:
                                logging.info('temperature below 55 degrees ')
                                

                        except Exception as e:
                            logging.critical('Error reading temperature: %s', e)

                        try:
                            logging.info('Check of tblControllo table (in for loop)')
                            conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                            cursor = conn.cursor()
                        
                            cursor.execute(self.queryRead)
                            row = cursor.fetchone()
                            value = row[1]
                            
                            if value==0:
                                logging.info('value = 0 -> restarting program and waiting for value= 1')
                                conn.close()
                                script_bash = "utilityFiles/reboot.sh"
                                subprocess.run(["bash", script_bash])
                            else:
                                logging.info('value = 1 -> continuing program execution')
                                
                        except Exception as e:
                            logging.error('Error during query execution: %s',e)
                            print(f"Error during query execution: {e}")
                            conn.rollback()
                        finally:
                            conn.close()
                    self.i+=1

                if day !=  datetime.today().date():
                    day=datetime.today().date()
                    fileLog='filesLog/'+str(day)+'.log'
                    logging.info('END OF DAY - CHANGING .LOG FILE')
                    logging.shutdown() 
                    os.rename(fileLog, 'filesLog/'+str(day)+'.log')  
                    logging.basicConfig(filename='filesLog/'+str(day)+'.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                    logging.info('NEW DAY - STARTING NEW .LOG FILE') 

        except Exception as e:
            logging.critical('ERROR GENERATED IN MAIN FOR LOOP : %s',e)
            try:
                conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                cursor = conn.cursor()
                n = datetime.now()
                stringa_data_ora = n.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(self.queryError,( str(e), str(stringa_data_ora)))
                conn.commit()
                logging.warning("Error reported on database")
            except Exception as er:
                logging.error('Error connecting to database: %s',er)
            finally:
                conn.close()

            logging.warning("RESTARTING PROGRAM - ATTEMPTING TO RESOLVE ERROR")
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
        logging.info("setting model - creating YOLO model object - model : %s",mod)
        self.modello = mod
        self.model = YOLO(self.modello)
        
        

#GUI control class
class Finestra(QtWidgets.QMainWindow):
    logging.info('Creating Window class - worker object - thread')
    work = Worker()
    thread = QThread()
    font = ""
    cont = True #only used to receive a value (not needed in this program) from startRead
    ctrlStart=True
    
    #object constructor of the class
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
          
        modelloScelto="modelli_in_uso/v8s2000.pt"
        self.work.setModel(modelloScelto)
            
        logging.info('connecting run function to thread')
        self.thread.started.connect(self.work.run)  #connects the thread to the function to be run
        
        logging.info('connecting signals to functions')
        #connecting signals to their functions
        self.work.txtObjInEdit.connect(self.update_line_in)
        self.work.txtObjOutEdit.connect(self.update_line_out)
        self.work.txtLavEdit.connect(self.update_line_lav) #modified with obj2 out
        self.work.pixmapSet.connect(self.update_pixmap)
        self.work.txtObjTotEdit.connect(self.update_tot) #continues to only write status running
        self.work.startLav.connect(self.update_lab) 
        self.work.obj2OutEdit.connect(self.updateOut) #added for obj1 out
        
        logging.info('setting fonts and GUI interface')
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
        

        #loading program text while waiting for webcam connection
        self.ui.label.setText("Waiting...")#Loading
        custom_font = QFont()
        custom_font.setPointSize(20)
        self.ui.label.setFont(custom_font)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        
        logging.info('first check of tblControllo table')

        log=0
        while self.ctrlStart:
                
                conn = pymssql.connect(server=self.work.server, user=self.work.username, password=self.work.password, database=self.work.database)
                cursor = conn.cursor()
                try:
                    cursor.execute(self.work.queryRead)
                    row = cursor.fetchone()
                    value = row[1]
                    
                    if value==1:
                        logging.info('value = 1 - ending while loop - starting thread with go bit set to True')
                        self.ctrlStart=False
                        self.thread.start() #starting the thread
                        self.work.go = True #starting processing
        
                except Exception as e:
                    logging.error('Error during query execution: %s',e)
                    print(f"Error during query execution: {e}")
                    conn.rollback()

                finally:
                    conn.close()
                
                if self.ctrlStart==True:
                    if(log%20==0):
                        if day !=  datetime.today().date():
                            day=datetime.today().date()
                            fileLog='filesLog/'+str(day)+'.log'
                            logging.info('END OF DAY - CHANGING .LOG FILE')
                            logging.shutdown() 
                            os.rename(fileLog, 'filesLog/'+str(day)+'.log')  
                            logging.basicConfig(filename='filesLog/'+str(day)+'.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                            logging.info('NEW DAY - STARTING NEW .LOG FILE')  

                    logging.info('value = 0 - Rechecking in 30 seconds...')
                    print("Value = 0 - Rechecking in 30 seconds...")
                    time.sleep(30)
                    log+=1



    #function that handles start button  
    def clickStart(self):
        why="removed for frames program"
       
    #function that handles stop button
    def clickStop(self):
        why="removed for frames program"
        
    #function that handles restart button  
    def clickRestart(self):
        why="removed for frames program"
    
    #save the total
    def saveTot(self):
        why="removed for frames program"
            
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
        self.ui.txtObjIn.setText("Number of obj1: " + text)
        self.ui.txtObjIn.setFont(self.font)
        
    def update_tot(self, text):
        self.ui.txtObjTot.setText("Status: Running")
        self.ui.txtObjTot.setFont(self.font)
    
    def update_line_out(self, text):
        self.ui.txtObjOut.setText("Number of obj2: " + text)
        self.ui.txtObjOut.setFont(self.font)
    
    def update_line_lav(self, text):
        self.ui.txtLav.setText("obj1 OUT : " + text)
        self.ui.txtLav.setFont(self.font)
        
    def update_pixmap(self, image):
        self.ui.label.setText("")
        self.ui.label.setPixmap(image)

    #added for OUT program modification
    def updateOut(self, text):
        self.ui.txtOb.setText("obj2 OUT : "+ text)
        self.ui.txtOb.setFont(self.font)


    def update_lab(self):
        self.ui.label.setText("Press Start to begin\nor\nchoose options in the Menu")
        custom_font = QFont()
        custom_font.setPointSize(20)
        self.ui.label.setFont(custom_font)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.groupBoxMenu.setEnabled(False) #CHANGED FOR FRAMES PROGRAM
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #48c75b;} ")##btnStart:hover{background-color: #ffffff;}
    
    
#main call
if __name__ == '__main__':

    app = QApplication(sys.argv)    #creating graphical application 
    time.sleep(1)   #waiting for app graphical creation

    app.setStyleSheet(Path('style.qss').read_text())    #calling qss file (python css)
    window = Finestra() #creating window object
    
    sys.exit(app.exec())    #command to execute the application
