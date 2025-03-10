# Garzoni Stefano 
#main program with GPIO
import sys
from PyQt5.QtWidgets import QWidget, QApplication,QMessageBox
from countingYoloRT import Ui_MainWindow
from keypad import Ui_Form
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import time
from pathlib import Path
from datetime import datetime
import cv2
from ultralytics import YOLO
import supervision as sv
import Jetson.GPIO as GPIO 

import subprocess   #library for program restart

#library for handling system file error
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

LINE_START = sv.Point(230, 480) #720, 0   |320, 0
LINE_END = sv.Point(230, 0)#720, 1000  |320, 480
RELAY_PIN = 7

#thread containing the for loop
class Worker(QObject):   
    #variable creation
    space = [0,0,1,0,0,0,0,0]
    go = False
    last = 0
    now = 0
    total = 0
    x = 0
    nLav = 1
    line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
    model = None
    modello = ""
    enter = "\n"
    start = "Processing n. "
    separatore = "------------------------------------------"
    first = 1
    start = True
    nCic=0
    crN=[]
    crC=[]
    
    #thread signal creation
    txtObjTotEdit = pyqtSignal(str) #signal to modify the total text field
    txtObjInEdit = pyqtSignal(str)  #signal to modify the counted objects text field
    txtObjOutEdit = pyqtSignal(str) #signal to modify the outgoing objects text field
    txtLavEdit = pyqtSignal(str)    #signal to modify the processing change text field
    pixmapSet = pyqtSignal(QPixmap) #signal to send video frames to the label
    stop = pyqtSignal() #signal to stop the program at the end of processing
    fineLav = pyqtSignal(str, str)  #signal to indicate the end of processing (useful for the message box)
    startLav = pyqtSignal() #signal to mark the start of processing
    write = pyqtSignal()
    
    #function containing the FOR loop for object detection
    def run(self):
        self.line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
        line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=1, text_scale=0.5)
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )
    
        self.model = YOLO(self.modello) 
        
        for result in self.model.track(source=0, stream=True, agnostic_nms=True, device=0, conf=0.5):
            if (self.nCic % 5 == 0 and self.nCic <= 275) :
                self.createProgram(self.crN[int(self.nCic/5)])
            elif (self.nCic %5==0 and self.nCic <=315):
                self.createProgram(self.space[int((self.nCic-280)/5)])
            elif (self.nCic %5==0 and self.nCic <=595):
                self.createProgram(self.crC[int((self.nCic-320)/5)])
            elif self.nCic == 608 :
                self.nCic=0
            self.nCic=self.nCic+1

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
                
                self.line_counter.trigger(detections=detections)
                line_annotator.annotate(frame=frame, line_counter=self.line_counter)
                self.now = self.line_counter.in_count
                
                if(self.now != self.last):
                    self.write_to_file('utilityFiles/count.txt', f'{self.enter}{self.line_counter.in_count}') 
                    self.total = self.total+(self.now-self.last)
                    
                    
                    
                self.last = self.line_counter.in_count
                
                #adapt frame image to QImage for display
                height, width, bytesPerComponent = frame.shape
                bytesPerLine = bytesPerComponent * width
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                image = QImage(frame_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)
                
                #signals emitted by the Thread
                self.pixmapSet.emit(QPixmap.fromImage(image))
                self.txtObjTotEdit.emit(str(self.total))
                self.txtObjInEdit.emit(str(self.line_counter.in_count))
                self.txtObjOutEdit.emit(str(self.line_counter.out_count))
                self.txtLavEdit.emit(str(self.nLav))
                
                #turn on the relay
                if self.first == 1:
                    GPIO.output(RELAY_PIN, GPIO.HIGH)
                    first = 0
                
                #check if processing is finished
                if self.x==self.line_counter.in_count:
                    self.now=0
                    self.last=0
                    self.go = False
                    self.stop.emit()
                    self.first = 1
                    
                    self.fineLav.emit("Processing finished", "Success")
        
                
    #control for the STOP function
    def setGo(self, b):
        self.go = b
        
    def write_to_file(self, file_path: str, line: str) -> None:
        with open(file_path, "a") as file:
            file.write(line + "\n") 

    def createProgram(self, cr):
        print((cr))
            
    def setModel(self, mod, n):
        self.modello = mod
        self.model = YOLO(self.modello)
        if(n!=0):
            self.fineLav.emit("The program will\nrestart to apply\nthe selected changes...", "Model Change")
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Reset")
            msg_box.setText("Changing object...\nReset the total piece count?")
    
            # Customize the dialog window size
            msg_box.setStyleSheet("QMessageBox { width: 400px;font-size: 30px; }")
            
            # Customize the "No" button
            no_button = msg_box.addButton("No", QMessageBox.NoRole)
            no_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px;}")
    
            # Customize the "Yes" button
            yes_button = msg_box.addButton("Yes", QMessageBox.YesRole)
            yes_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px; }")
            
            # Handle button clicks
            msg_box.exec_()
            if msg_box.clickedButton() == yes_button:
                self.total=0
                self.write.emit()   #save choices
            # Path to the Bash script to execute
            script_bash = "utilityFiles/riavvio.sh"
            
            # Execute the Bash script
            subprocess.run(["bash", script_bash])
        
        

#class for GUI control
class Finestra(QtWidgets.QMainWindow):
    work = Worker()
    thread = QThread()
    start = "Processing n. "
    enter = "\n"
    font = ""
    separatore = "------------------------------------------"
    tast = None
    cont = True
    
    #constructor of the class object
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupMainWindow(self)
        
        self.showFullScreen()
        self.work.crN=self.ui.createrValueN
        self.work.crC=self.ui.createrValueC
        
        #connect events to buttons and widgets
        self.ui.btnStart.clicked.connect(self.clickStart)
        self.ui.btnStop.clicked.connect(self.clickStop)
        self.ui.btnRestart.clicked.connect(self.clickRestart)
        self.ui.actionMenu.triggered.connect(self.changeWinMenu)
        self.ui.actionSave.triggered.connect(self.saveTot)
        self.ui.txtObPezzi.mousePressEvent = self.tastierino


        self.ui.groupBoxMenu.setHidden(True) #hide menu window
        self.ui.actionSave.setEnabled(False) #disable save action
        self.ui.groupBoxMenu.setEnabled(False)  #disable menu window

        
        self.work.moveToThread(self.thread) #move the Work class to a thread
        
        cont, self.last,self.mod, tot=self.StartRead()  #function to read the last choices
        self.work.total=int(tot)    
        
        if(cont == 0):  #if there are last choices in the file
            self.ui.txtObPezzi.setPlainText(str(self.last))
            self.work.x = str(self.last)
            self.setCheck()
            
        self.work.setModel(self.getChecked(),0)
            
        
        self.thread.started.connect(self.work.run)  #connect the thread to the function to run
        
        #connect signals to their functions
        self.work.txtObjInEdit.connect(self.update_line_in)
        self.work.txtObjOutEdit.connect(self.update_line_out)
        self.work.txtLavEdit.connect(self.update_line_lav)
        self.work.pixmapSet.connect(self.update_pixmap)
        self.work.stop.connect(self.clickStop)
        self.work.fineLav.connect(self.showMsg)
        self.work.txtObjTotEdit.connect(self.update_tot)
        self.work.startLav.connect(self.update_lab) 
        self.work.write.connect(self.write_change_model)
        
        #set fonts for widgets
        self.font = self.ui.txtOb.font()
        self.font.setPointSize(24)
        self.ui.txtObjIn.setFont(self.font)
        self.ui.txtObjOut.setFont(self.font)
        self.ui.txtOb.setFont(self.font)
        self.ui.txtLav.setFont(self.font)
        self.ui.txtObjTot.setFont(self.font)
        
        #set fonts for radio buttons
        font1 = QFont()
        font1.setPointSize(30)
        for valori in self.ui.radioButtons.values() :   
            for valore in valori:
                valore.setFont(font1)
        
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #a3a8a5;}")
        self.ui.btnStop.setStyleSheet("#btnStop{background-color: #a3a8a5;}")
        self.ui.btnRestart.setStyleSheet("#btnRestart{background-color: #a3a8a5;}")
        
        #function to create and activate pulse
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        
        GPIO.output(RELAY_PIN, GPIO.LOW)
        
        #program loading text while waiting for webcam connection
        self.ui.label.setText("Loading...")
        custom_font = QFont()
        custom_font.setPointSize(20)
        self.ui.label.setFont(custom_font)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.thread.start() #start the thread
        
        self.write_to_file("utilityFiles/count.txt", "\nObject: "+self.getNomeRadioBtn()+"\n")


    #function to handle the start button  
    def clickStart(self):
        if self.ui.txtObPezzi.toPlainText().isdigit():  #if target pieces is a number and not a string
            self.WriteStartChoose(self.ui.txtObPezzi.toPlainText(), self.getChecked(), self.work.total) #write the choices as last choices
            if self.work.line_counter.in_count < int(self.ui.txtObPezzi.toPlainText()) or self.work.x == self.work.line_counter.in_count: #self.work.x = target within the thread | self.ui.txtObPezzi.toPlainText()=user modified target
                if self.work.modello != self.getChecked():  #if the model has changed
                    self.WriteStartChoose(self.ui.txtObPezzi.toPlainText(),self.getChecked(),self.work.total)   #save choices
                    self.work.setModel(self.getChecked(),1) #call function
                
                #enable and disable buttons
                self.ui.btnStart.setEnabled(False)
                self.ui.btnRestart.setEnabled(False)
                self.ui.btnStop.setEnabled(True)
                self.ui.btnStart.setStyleSheet("#btnStart{background-color: #a3a8a5;}")
                self.ui.btnStop.setStyleSheet("#btnStop{background-color: #c74c48;} #btnStop:hover{background-color: #ffffff;}")
                self.ui.btnRestart.setStyleSheet("#btnRestart{background-color: #a3a8a5;}")
                
                if self.cont == True: #if it is the first time pressing start
                    #write the first processing in the file
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    self.write_to_file('utilityFiles/count.txt', f'{self.separatore}{self.enter}{self.start}{self.work.nLav} {dt_string}')

                    #set the target selected by the user
                    self.work.x = int(self.ui.txtObPezzi.toPlainText())

                    self.cont = False #cont false, only true for the first time
                    self.work.go = True #start processing

                elif self.work.x == self.work.line_counter.in_count: #if processing is finished
                    self.work.nLav+=1 #increase processing
                    self.work.x = int(self.ui.txtObPezzi.toPlainText()) #set the target selected by the user
                    
                    #write the first processing in the file
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    self.write_to_file('utilityFiles/count.txt', f'{self.separatore}{self.enter}{self.start}{self.work.nLav} {dt_string}')
                    
                    #reset line counters
                    self.work.line_counter.in_count = 0
                    self.work.line_counter.out_count = 0
                    
                    self.work.setGo(True) #start processing
                else:
                    #set the target selected by the user
                    self.work.x = int(self.ui.txtObPezzi.toPlainText())
                    
                    #start processing
                    self.work.setGo(True)
                    
               
                
                #set text field with the target
                self.ui.txtOb.setText("Target pieces: " + str(self.work.x)) 
                self.ui.txtOb.setFont(self.font)

                #disable menu
                self.ui.groupBoxMenu.setEnabled(False)
            
            elif self.work.line_counter.in_count == int(self.ui.txtObPezzi.toPlainText()): #if the selected target is equal to the one reached in processing
                #warn the user
                self.show_alert_endLav()
                
            else: #if the selected target is less than the one reached in processing
                #warn the user
                self.showMsg("The processing has already\nreached the set target", "Attention")
        
        else: #if the value entered by the user is not a number
            #warn the user
            self.showMsg("Enter a valid number\nin 'Target pieces'", "Error")
            
    #function to handle the stop button
    def clickStop(self):
        #enable buttons
        GPIO.output(RELAY_PIN, GPIO.LOW) #stop the relay
        self.ui.groupBoxMenu.setEnabled(True) #enable menu
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStop.setEnabled(False)
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #48c75b;} #btnStart:hover{background-color: #ffffff;}")
        self.ui.btnStop.setStyleSheet("#btnStop{background-color: #a3a8a5;}")
        
        if self.work.x != self.work.line_counter.in_count and self.work.line_counter.in_count!=0: #if processing is not finished also enable restart
            self.ui.btnRestart.setEnabled(True)
            self.ui.btnRestart.setStyleSheet("#btnRestart{background-color: #4889c7;} #btnRestart:hover{background-color: #ffffff;}")
        
        self.work.setGo(False) #stop processing

        
    #function to handle the restart button  
    def clickRestart(self):
        if self.ui.txtObPezzi.toPlainText().isdigit(): #if target pieces is a number and not a string
            if self.work.modello != self.getChecked(): #if the model has changed
                self.WriteStartChoose(self.ui.txtObPezzi.toPlainText(),self.getChecked(),self.work.total) #write the last choices to the file
                self.work.setModel(self.getChecked(),1) #change the model
            
            self.WriteStartChoose(self.ui.txtObPezzi.toPlainText(), self.getChecked(), self.work.total) #write the last choices to the file

            #enable and disable buttons
            self.ui.btnStart.setEnabled(False)
            self.ui.btnRestart.setEnabled(False)
            self.ui.btnStop.setEnabled(True)
            self.ui.btnStart.setStyleSheet("#btnStart{background-color: #a3a8a5;}")
            self.ui.btnStop.setStyleSheet("#btnStop{background-color: #c74c48;} #btnStop:hover{background-color: #ffffff;}")
            self.ui.btnRestart.setStyleSheet("#btnRestart{background-color: #a3a8a5;}")
            
            self.work.x = int(self.ui.txtObPezzi.toPlainText()) #set the target selected by the user
            
            self.show_confirmation_dialog() #ask if the user wants to save the processing or delete it

            #reset values
            self.work.now = 0
            self.work.last = 0
            self.work.line_counter.in_count = 0
            self.work.line_counter.out_count = 0
            
            self.work.setGo(True) #restart processing
            
            #set the target selected in the text field
            self.ui.txtOb.setText("Target pieces: " + str(self.work.x))
            self.ui.txtOb.setFont(self.font)

            self.ui.groupBoxMenu.setEnabled(False) #disable menu
        
        else: #if the value entered by the user is not a number
            #warn the user
            self.showMsg("Enter a valid number\nin 'Target pieces'", "Error")
            
    #function to switch from view to menu
    def changeWinMenu(self):
        if self.ui.groupBoxView.isHidden() == False:    #if the menu is hidden
            self.ui.groupBoxView.setHidden(True)
            self.ui.groupBoxMenu.setHidden(False)
            self.ui.actionMenu.setText("View")
        else:   
            self.ui.groupBoxView.setHidden(False)
            self.ui.groupBoxMenu.setHidden(True)
            self.ui.actionMenu.setText("Menu")
    
    #save the total
    def saveTot(self):
    
        self.clickStop()
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Reset")
        msg_box.setText("Saving will import the total number of pieces processed so far into memory and reset the 'Total Pieces' entry\nSave?")

        # Customize the dialog window size
        msg_box.setStyleSheet("QMessageBox { width: 400px;font-size: 30px; }")
        
        # Customize the "No" button
        no_button = msg_box.addButton("No", QMessageBox.NoRole)
        no_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px;}")

        # Customize the "Yes" button
        yes_button = msg_box.addButton("Yes", QMessageBox.YesRole)
        yes_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px; }")
        
        # Handle button clicks
        msg_box.exec_()
        if msg_box.clickedButton() == yes_button:   #if the user clicks 'yes' print the total to the file and then reset it
            self.write_to_file("utilityFiles/count.txt", "\ntotal : "+str(self.work.total)+ " day : "+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"\n")
            self.work.total=0
        

    #  FUNCTIONS CONNECTED TO SIGNALS TO UPDATE TEXT FIELDS AND LABELS

    def update_line_in(self, text):
        self.ui.txtObjIn.setText("Counted Pieces: " + text)
        self.ui.txtObjIn.setFont(self.font)
        
    def update_tot(self, text):
        self.ui.txtObjTot.setText("Total Pieces: " + text)
        self.ui.txtObjTot.setFont(self.font)
    
    def update_line_out(self, text):
        self.ui.txtObjOut.setText("Outgoing Pieces: " + text)
        self.ui.txtObjOut.setFont(self.font)
    
    def update_line_lav(self, text):
        self.ui.txtLav.setText("Processing number: " + text)
        self.ui.txtLav.setFont(self.font)
        
    def update_pixmap(self, image):
        self.ui.label.setText("")
        self.ui.label.setPixmap(image)

    def update_lab(self):
        self.ui.label.setText("Press Start to begin\nor\nchoose options in the Menu")
        custom_font = QFont()
        custom_font.setPointSize(20);
        self.ui.label.setFont(custom_font)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.groupBoxMenu.setEnabled(True)
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #48c75b;} #btnStart:hover{background-color: #ffffff;}")
        self.ui.actionSave.setEnabled(True)
    

    #get the value of the selected radio button (model)
    def getChecked(self):
        for chiave, valore in self.ui.radioButtons.items():
            if valore[0].isChecked():
                return chiave
    
    def getNomeRadioBtn(self):
        for valori in self.ui.radioButtons.values() :   
            for valore in valori:
                if valore.isChecked() == True:
                    return valore.text()
    
    #set the correct radio button (model) read from the last choices file
    def setCheck(self):
        for chiave, valori in self.ui.radioButtons.items():
            if chiave==self.mod:
                for valore in valori:
                    valore.setChecked(True)
    
    #function of the keypad
    def tastierino(self, event):
        #show the keypad and handle events
        self.tast.show()
        self.tast.ui.txtValore.setPlainText("")
        self.tast.ui.btnOk.clicked.connect(self.salva)
        self.tast.ui.btnClose.clicked.connect(self.chiudi)
    
    #close keypad
    def chiudi(self):
        self.ui.actionMenu.setEnabled(True)
        self.ui.groupBoxMenu.setEnabled(True)
        self.tast.close()
    
    #save choice entered from the keypad
    def salva(self):
        if len(self.tast.ui.txtValore.toPlainText()) > 0 and self.tast.ui.txtValore.toPlainText() != "0":
            self.ui.txtObPezzi.setPlainText(self.tast.ui.txtValore.toPlainText())
        self.tast.close()
        self.ui.groupBoxMenu.setEnabled(True)
        self.ui.actionMenu.setEnabled(True)
    
    #write data in processing to the file
    def write_to_file(self, file_path: str, line: str) -> None:
        with open(file_path, "a") as file:
            file.write(line + "\n")
    
    #write the last choices to the file
    def WriteStartChoose(self, data1, data2, data3):
        try:
            with open("utilityFiles/last.txt", 'w') as file:
                file.write(f"{data1};{data2};{data3}\n")
            print("Writing to file completed.")
        except Exception as e:
            print("An error occurred while writing to the file:", e)

    #read the last choices from the file (at program startup)      
    def StartRead(self):
        try:
            with open("utilityFiles/last.txt", 'r') as file:
                content = file.read()
                if( len(content.strip()) == 0 ) : #or len(content.strip()) == 1
                    return 1, None, None, None  # The file is empty
                else:
                    data1, data2, data3 = content.strip().split(';')
                    return 0, data1, data2, data3  # The file contains data
        except FileNotFoundError:
            print("File not found.")
            return -1, None, None, None  # Error code if the file does not exist or is not accessible
        except Exception as e:
            print("An error occurred:", e)
            return -1, None, None, None  # Generic error code
            
    def write_change_model(self):
        self.WriteStartChoose(self.ui.txtObPezzi.toPlainText(),self.getChecked(),self.work.total)   #save choices
    
    #generic function for the message box
    def showMsg(self, txt, title):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(txt)
        msg.setStyleSheet("QLabel{min-width:400px; font-size: 30px; min-height:100px;} QPushButton{ width:100px; height: 50px; font-size: 18px; }")
        msg.exec_()

    #message box created for restart (save the total?)
    def show_confirmation_dialog(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Reset")
        msg_box.setText("Save the counts found so far?")

        # Customize the dialog window size
        msg_box.setStyleSheet("QMessageBox { width: 400px;font-size: 30px; }")
        
        # Customize the "No" button
        no_button = msg_box.addButton("No", QMessageBox.NoRole)
        no_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px;}")

        # Customize the "Yes" button
        yes_button = msg_box.addButton("Yes", QMessageBox.YesRole)
        yes_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px; }")
        
        # Handle button clicks
        msg_box.exec_()
        if msg_box.clickedButton() == yes_button:   #if the choice is 'yes' write the data to the file and move to a new processing
            self.work.nLav+=1
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            self.write_to_file('utilityFiles/count.txt', f'{self.separatore}{self.enter}{self.start}{self.work.nLav} {dt_string}')
    
    #alert that warns that changing the target while the program is running will end the processing
    def show_alert_endLav(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Attention")
        msg_box.setText("Target pieces set equal\nto the number reached in processing,\nprocessing will end,\nContinue? ")

        # Customize the dialog window size
        msg_box.setStyleSheet("QMessageBox { width: 400px;font-size: 30px; }")
        
        # Customize the "No" button
        no_button = msg_box.addButton("No", QMessageBox.NoRole)
        no_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px;}")

        # Customize the "Yes" button
        yes_button = msg_box.addButton("Yes", QMessageBox.YesRole)
        yes_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px; }")

        # Handle button clicks
        msg_box.exec_()
        if msg_box.clickedButton() == yes_button:
            self.ui.btnStart.setEnabled(False)
            self.ui.btnRestart.setEnabled(False)
            self.ui.btnStop.setEnabled(True)
            self.ui.btnStart.setStyleSheet("#btnStart{background-color: #a3a8a5;}")
            self.ui.btnStop.setStyleSheet("#btnStop{background-color: #c74c48;} #btnStop:hover{background-color: #ffffff;}")
            self.ui.btnRestart.setStyleSheet("#btnRestart{background-color: #a3a8a5;}")
            self.work.x = int(self.ui.txtObPezzi.toPlainText())
            self.work.setModel(self.getChecked(),0)
            self.work.setGo(True)
        
            self.ui.txtOb.setText("Target pieces: " + str(self.work.x))
            #self.ui.txtMod.setText("Model: " + self.work.modello)
            self.ui.txtOb.setFont(self.font)
            #self.ui.txtMod.setFont(self.font)
            self.ui.groupBoxMenu.setEnabled(False)


#class to create keypad
class Tastierino(QWidget):
    #font = QFont()
    lista = None
    listaInd = None
    
    def __init__(self, parent): #constructor of the keypad
        super().__init__(parent)
        
        #events and handling
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)
        
        self.lista = [self.ui.btn0, self.ui.btn1, self.ui.btn2, self.ui.btn3, self.ui.btn4, self.ui.btn5, self.ui.btn6, self.ui.btn7, self.ui.btn8, self.ui.btn9]
        
        self.lista[0].clicked.connect(lambda: self.btnClick(0))
        self.lista[1].clicked.connect(lambda: self.btnClick(1))
        self.lista[2].clicked.connect(lambda: self.btnClick(2))
        self.lista[3].clicked.connect(lambda: self.btnClick(3))
        self.lista[4].clicked.connect(lambda: self.btnClick(4))
        self.lista[5].clicked.connect(lambda: self.btnClick(5))
        self.lista[6].clicked.connect(lambda: self.btnClick(6))
        self.lista[7].clicked.connect(lambda: self.btnClick(7))
        self.lista[8].clicked.connect(lambda: self.btnClick(8))
        self.lista[9].clicked.connect(lambda: self.btnClick(9))
        self.ui.btnDel.clicked.connect(self.delete)

    #function on keypad click
    def btnClick(self, i):
        self.ui.txtValore.setPlainText(self.ui.txtValore.toPlainText() + str(i))

    #function on delete click on keypad 
    def delete(self):
        if len(self.ui.txtValore.toPlainText()) > 0:
            self.ui.txtValore.setPlainText(self.ui.txtValore.toPlainText()[:-1])
    
#call main
if __name__ == '__main__':

    app = QApplication(sys.argv)    #create GUI application
    time.sleep(1)   #wait for the GUI app to be created

    app.setStyleSheet(Path('style.qss').read_text())    #call the qss file (python css)
    window = Finestra() #create the window object
    window.tast = Tastierino(window)    #create the keypad object as a child of window
    
    sys.exit(app.exec())    #command to run the application
