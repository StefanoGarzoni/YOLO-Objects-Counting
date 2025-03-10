#MAIN DEL PROGRAMMA CON CONTEGGIO DEGLI OUT
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
from line_zoneOUT import LineZoneNew #file con conteggio out: line_zoneOUT.py
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


#thread contenente il for
class Worker(QObject):   
    #creazione variabili
    logging.info('Creazione classe worker')
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
    ganciOut=0
    telaiOut=0
    er=0
    lastT=0
    lastG=0
    lastTo=0
    lastGo=0

    server = "192.168.7.226\sqlexpress"
    database = "ScambioVisione"
    username = "visione"
    password = "Visione123!"
    queryOut="UPDATE tblScambioVisioneOut SET Bilancelle = %d, Telai = %s, BilancelleOut= %s, TelaiOut= %s WHERE IduScambioVisione = 10" #query per aggiornamento OUT
    query = "UPDATE tblScambioVisione SET Bilancelle = %d, Telai = %s WHERE IduScambioVisione = 10" 
    queryLettura= "SELECT * FROM tblControllo"
    queryError="INSERT INTO tbllogErrori (Errore, DataOra) VALUES (%s, %s)"
    
    logging.info('Collegamento impulsi')
    #creazione impulsi del thread
    txtObjTotEdit = pyqtSignal(str) #impulso per modificare il campo di testo del totale
    txtObjInEdit = pyqtSignal(str)  #impulso per modificare il campo di testo degli oggetti contati
    txtObjOutEdit = pyqtSignal(str) #impulso per modificare il campo di testo degli oggetti in uscita
    txtLavEdit = pyqtSignal(str)    #impulso per modificare il campo di testo del cambio lavorazione
    pixmapSet = pyqtSignal(QPixmap) #impulso per inviare alla label i frame del video
    startLav = pyqtSignal() #impulso per segnare che inizia la lavorazione
    telaiOutEdit = pyqtSignal(str)
    
    
    #funzione contenente il FOR della detection Object
    def run(self):

        global day
        global fileLog

        logging.info('avvio metodo run')

        self.go = True #starto la lavorazione
        self.line_counter = LineZoneNew(start=LINE_START, end=LINE_END)
        line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=1, text_scale=0.5)
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )

        logging.info('recupero dei dati dai file telai.txt e ganci.txt')
        if self.er==0:
            self.er=1
            try:
                with open("utilityFiles/telai.txt", 'r') as file:
                    content = file.read()
                self.line_counter.in_count=int(content)
                self.telai=int(content)
                self.total=int(content)
                self.lastT=self.total

                with open("utilityFiles/ganci.txt", 'r') as file:
                    content = file.read()
                self.ganci=int(content)
                self.lastG=self.ganci

                with open("utilityFiles/ganciOut.txt", 'r') as file:
                    content = file.read()
                self.ganciOut=int(content)
                self.lastGo=self.ganciOut

                with open("utilityFiles/telaiOut.txt", 'r') as file:
                    content = file.read()
                self.telaiOut=int(content)
                self.lastTo=self.telaiOut
                self.line_counter.out_count=(self.lastTo+self.lastGo)

            except Exception as e:
                logging.warning("Errore nella lettura dei file - Attenzione il conteggio telai e ganci parte da 0\n - errore: %s",e)


        logging.info('avvio del ciclo for principale')
        try:

            for result in self.model.track(source=0, stream=True, agnostic_nms=True, device=0, conf=0.5):

                logging.info('Ciclo n: %d',self.i)
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

                    
                    #adattamento frame immagine a QImage per mostrarlo
                    height, width, bytesPerComponent = frame.shape
                    bytesPerLine = bytesPerComponent * width
                    
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    image = QImage(frame_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)
                    
                    for id in ris:
                        if id==-1:
                            continue
                        if id==1: #id telaio=1 id bottle=39
                            self.telai+=1
                            logging.info('incremento contatore telai : (%d)',self.telai)
                        else :
                            if id==0: #id gancio=0 id telefono=67
                                self.ganci+=1
                                logging.info('incremento contatore ganci : (%d)',self.ganci)

                    for id1 in ris_out:
                        if id1==-1:
                            continue
                        if id1==1: #id telaio=1 id bottle=39
                            self.telaiOut+=1
                            logging.info('numero telai out : (%d)',self.telaiOut)
                        else :
                            if id1==0: #id gancio=0 id telefono=67
                                self.ganciOut+=1
                                logging.info('numero ganci out : (%d)',self.ganciOut)
                    ctrlValue=0
                    if self.lastT!= self.telai or self.lastG!=self.ganci:
                        logging.info('cambio valore delle variabili ganci e telai -> scrivo nei files')
                        #scrittura su file
                        self.write_to_file_gt("utilityFiles/ganci.txt", f'{self.ganci}')
                        self.write_to_file_gt("utilityFiles/telai.txt", f'{self.telai}')
                        ctrlValue=1
                    
                    if self.lastTo!= self.telaiOut or self.lastGo!=self.ganciOut:
                        logging.info('cambio valore delle variabili ganci e telai OUT -> scrivo nei files')
                        self.write_to_file_gt("utilityFiles/ganciOut.txt", f'{self.ganciOut}')
                        self.write_to_file_gt("utilityFiles/telaiOut.txt", f'{self.telaiOut}')
                        ctrlValue=1

                    if(ctrlValue==1):
                        #query
                        conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                        cursor = conn.cursor()
                        
                        try:
                            logging.info('aggiorno il database')
                            cursor.execute(self.queryOut,(str(self.ganci), str(self.telai), str(self.ganciOut), str(self.telaiOut)))
                            conn.commit()
                            

                        except Exception as e:
                            logging.error('Errore durante l esecuzione della query: %s',e)
                            print(f"Errore durante l'esecuzione della query: {e}")
                            conn.rollback()

                        finally:
                            conn.close()

                    self.lastT=self.telai
                    self.lastG=self.ganci
                    self.total=self.telai
                    self.lastTo=self.telaiOut
                    self.lastGo=self.ganciOut
                    
                    logging.info('emissione degli impulsi di aggiornamento dati - file e interfaccia grafica')
                    #impulsi emessi dal Thread
                    self.pixmapSet.emit(QPixmap.fromImage(image))
                    self.txtObjTotEdit.emit(str(self.total))
                    self.txtObjInEdit.emit(str(self.telai))
                    self.txtObjOutEdit.emit(str(self.ganci))
                    self.txtLavEdit.emit(str(self.ganciOut)) #impulso ganci out
                    self.telaiOutEdit.emit(str(self.telaiOut)) #impulso telai out

                    if(self.i%700==0 and self.i!=0):
                        try:
                            logging.info('Lettura del file contenente la temperatura')
                            try:
                                with open("/sys/devices/virtual/thermal/thermal_zone0/temp") as temp_file:
                                    temp = temp_file.read().strip()
                                    temp_celsius = float(temp) / 1000.0 #conversione
                                logging.info("temperatura registrata: %s",temp_celsius)
                            except Exception as e:
                                temp_celsius=0.0
                                logging.error("Errore durante il recupero della temperatura della CPU dal file :", e)

                            if(temp_celsius>=55 and temp_celsius<70):
                                logging.info('temperature oltre i 55 gradi')
                                
                            elif temp_celsius>=70 and temp_celsius <78:
                                logging.info('temperature oltre i 70 gradi')
                                
                            elif temp_celsius>=78 and temp_celsius <85:
                                logging.info('temperature oltre i 78 gradi')
                               
                            elif temp_celsius>=85:
                                logging.error('temperature oltre i 85 gradi -> blocco del ciclo for')
                                try:
                                    conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                                    cursor = conn.cursor()
                                    n = datetime.now()
                                    stringa_data_ora = n.strftime("%Y-%m-%d %H:%M:%S")
                                    cursor.execute(self.queryError,( 'temperature oltre i 85 gradi -> blocco del ciclo for', str(stringa_data_ora)))
                                    conn.commit()
                                    logging.warning("Errore segnalato sul database")
                                except Exception as er:
                                    logging.error('Errore durante la connessione al database: %s',er)
                                finally:
                                    conn.close()
                                    ctrlTemp=True
                                    while ctrlTemp:
                                        self.pixmapSet.emit("errore : attesa temperatura adeguata\nContattare un tecnico") #test aggiornamento label video
                                        time.sleep(60)
                                        logging.warning('Lettura del file contenente la temperatura in attesa che sia sotto i 80 gradi')
                                        try:
                                            with open("/sys/devices/virtual/thermal/thermal_zone0/temp") as temp_file:
                                                temp = temp_file.read().strip()
                                                temp_celsius = float(temp) / 1000.0 #conversione
                                            if temp_celsius < 70:
                                                logging.warning("temperatura abbassata : %s", temp_celsius)
                                                ctrlTemp=False
                                            else:
                                                logging.warning("ritento tra 1m | temperatura NON abbastanza basse : %s", temp_celsius)
                                        except Exception as e: 
                                            logging.error("errore nella lettura del file temperature %s",e)


                            else:
                                logging.info('temperatura minore di 55 gradi ')
                                

                        except Exception as e:
                            logging.critical('Errore nella lettura della temperatura: %s', e)

                        try:
                            logging.info('Check della tabella tblControllo (nel for)')
                            conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                            cursor = conn.cursor()
                        
                            cursor.execute(self.queryLettura)
                            row = cursor.fetchone()
                            value = row[1]
                            
                            if value==0:
                                logging.info('value = 0 -> riavvio del programma e attesa value= 1')
                                conn.close()
                                script_bash = "utilityFiles/riavvioOUT.sh"
                                subprocess.run(["bash", script_bash])
                            else:
                                logging.info('value = 1 -> continuo esecuzione del programma')
                                
                        except Exception as e:
                            logging.error('Errore durante l esecuzione della query: %s',e)
                            print(f"Errore durante l'esecuzione della query: {e}")
                            conn.rollback()
                        finally:
                            conn.close()
                    self.i+=1

                if day !=  datetime.today().date():
                    day=datetime.today().date()
                    fileLog='filesLog/'+str(day)+'.log'
                    logging.info('FINE GIORNO - CAMBIO DEL FILE .LOG')
                    logging.shutdown() 
                    os.rename(fileLog, 'filesLog/'+str(day)+'.log')  
                    logging.basicConfig(filename='filesLog/'+str(day)+'.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                    logging.info('CAMBIO GIORNO - INIZIO NUOVO FILE .LOG') 

        except Exception as e:
            logging.critical('ERRORE GENERATO NEL FOR PRINCIPALE : %s',e)
            try:
                conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                cursor = conn.cursor()
                n = datetime.now()
                stringa_data_ora = n.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(self.queryError,( str(e), str(stringa_data_ora)))
                conn.commit()
                logging.warning("Errore segnalato sul database")
            except Exception as er:
                logging.error('Errore durante la connessione al database: %s',er)
            finally:
                conn.close()

            logging.warning("RIAVVIO PROGRAMMA - TENTATIVO DI RISOLVERE L'ERRORE")
            script_bash = "utilityFiles/riavvioOUT.sh"
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
        logging.info("settaggio del modello - ceazione oggetto YOLO model - modello : %s",mod)
        self.modello = mod
        self.model = YOLO(self.modello)
        
        

#classe di controllo interfaccia grafica
class Finestra(QtWidgets.QMainWindow):
    logging.info('Creazione della classe Finestra - oggetto worker - thread')
    work = Worker()
    thread = QThread()
    font = ""
    cont = True #serve solo per ricevere un valore (che non serve in questo programma) da startRead
    ctrlStart=True
    
    #costruttore dell'oggetto della classe
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupMainWindow(self)
        
        self.showFullScreen()
        self.work.crN=self.ui.createrValueN
        self.work.crC=self.ui.createrValueC
        
        global day
        global fileLog

        #connessione degli eventi ai bottoni e widget
        self.ui.btnStart.clicked.connect(self.clickStart)
        self.ui.btnStop.clicked.connect(self.clickStop)
        self.ui.btnRestart.clicked.connect(self.clickRestart)
        self.ui.actionMenu.triggered.connect(self.changeWinMenu)
        self.ui.actionSave.triggered.connect(self.saveTot)

        self.ui.groupBoxMenu.setHidden(True) #nasconde la finestra menu
        self.ui.actionSave.setEnabled(False) #disattiva azione salva
        self.ui.groupBoxMenu.setEnabled(False)  #disattiva la finestra menu

        
        self.work.moveToThread(self.thread) #sposta la classe Work in un thread
          
        modelloScelto="modelli_in_uso/v8s2000.pt"
        self.work.setModel(modelloScelto)
            
        logging.info('connessione della funzione run al thread')
        self.thread.started.connect(self.work.run)  #connette il thread alla funzione da runnare
        
        logging.info('connessione degli impulsi alle funzioni')
        #conetto gli impulsi alle loro funzioni
        self.work.txtObjInEdit.connect(self.update_line_in)
        self.work.txtObjOutEdit.connect(self.update_line_out)
        self.work.txtLavEdit.connect(self.update_line_lav) #modificata con ganci out
        self.work.pixmapSet.connect(self.update_pixmap)
        self.work.txtObjTotEdit.connect(self.update_tot) #continua solo a scrivere status running
        self.work.startLav.connect(self.update_lab) 
        self.work.telaiOutEdit.connect(self.updateOut) #aggiunta per telai out
        
        logging.info('settaggio dei font e dell interfaccia grafica')
        #settaggio dei font per i widget
        self.font = self.ui.txtOb.font()
        self.font.setPointSize(24)
        self.ui.txtObjIn.setFont(self.font)
        self.ui.txtObjOut.setFont(self.font)
        self.ui.txtOb.setFont(self.font)
        self.ui.txtLav.setFont(self.font)
        self.ui.txtObjTot.setFont(self.font)
        
        #setto i font ai radio button
        font1 = QFont()
        font1.setPointSize(30)
        for valori in self.ui.radioButtons.values() :   
            for valore in valori:
                valore.setFont(font1)
        
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #48c75b;}")
        self.ui.btnStop.setStyleSheet("#btnStop{background-color: #a3a8a5;}")
        self.ui.btnRestart.setStyleSheet("#btnRestart{background-color: #a3a8a5;}")
        

        #testo del caricamento del programma in attesa della connessione alla webcam
        self.ui.label.setText("Attendo...")#Caricamento
        custom_font = QFont()
        custom_font.setPointSize(20)
        self.ui.label.setFont(custom_font)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        
        logging.info('primo check della tabella tblControllo')

        log=0
        while self.ctrlStart:
                
                conn = pymssql.connect(server=self.work.server, user=self.work.username, password=self.work.password, database=self.work.database)
                cursor = conn.cursor()
                try:
                    cursor.execute(self.work.queryLettura)
                    row = cursor.fetchone()
                    value = row[1]
                    
                    if value==1:
                        logging.info('value = 1 - termino il ciclo while - start del thread con bit go messo a True')
                        self.ctrlStart=False
                        self.thread.start() #starto il thread
                        self.work.go = True #starto la lavorazione
        
                except Exception as e:
                    logging.error('Errore durante l esecuzione della query: %s',e)
                    print(f"Errore durante l'esecuzione della query: {e}")
                    conn.rollback()

                finally:
                    conn.close()
                
                if self.ctrlStart==True:
                    if(log%20==0):
                        if day !=  datetime.today().date():
                            day=datetime.today().date()
                            fileLog='filesLog/'+str(day)+'.log'
                            logging.info('FINE GIORNO - CAMBIO DEL FILE .LOG')
                            logging.shutdown() 
                            os.rename(fileLog, 'filesLog/'+str(day)+'.log')  
                            logging.basicConfig(filename='filesLog/'+str(day)+'.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                            logging.info('CAMBIO GIORNO - INIZIO NUOVO FILE .LOG')  

                    logging.info('value = 0 - Ricontrollo tra 30 secondi...')
                    print("Value = 0 - Ricontrollo tra 30 secondi...")
                    time.sleep(30)
                    log+=1



    #funzione che gestisce il bottone start  
    def clickStart(self):
        perche="tolta per programma telai"
       
    #funzione che gestisce il bottone stop
    def clickStop(self):
        perche="tolta per programma telai"
        
    #funzione che gestisce il bottone restart  
    def clickRestart(self):
        perche="tolta per programma telai"
    
    #salvo il totale
    def saveTot(self):
        perche="tolta per programma telai"
            
    #funzione per il passaggio dalla view al menu
    def changeWinMenu(self):
        if self.ui.groupBoxView.isHidden() == False:    #se il menu è nascosto
            self.ui.groupBoxView.setHidden(True)
            self.ui.groupBoxMenu.setHidden(False)
            self.ui.actionMenu.setText("View")
        else:   
            self.ui.groupBoxView.setHidden(False)
            self.ui.groupBoxMenu.setHidden(True)
            self.ui.actionMenu.setText("Menu")
    

    def update_line_in(self, text):
        self.ui.txtObjIn.setText("Numero Telai: " + text)
        self.ui.txtObjIn.setFont(self.font)
        
    def update_tot(self, text):
        self.ui.txtObjTot.setText("Status: Running")
        self.ui.txtObjTot.setFont(self.font)
    
    def update_line_out(self, text):
        self.ui.txtObjOut.setText("Numero Ganci: " + text)
        self.ui.txtObjOut.setFont(self.font)
    
    def update_line_lav(self, text):
        self.ui.txtLav.setText("Ganci OUT : " + text)
        self.ui.txtLav.setFont(self.font)
        
    def update_pixmap(self, image):
        self.ui.label.setText("")
        self.ui.label.setPixmap(image)

    #aggiunta per modifica programma OUT
    def updateOut(self, text):
        self.ui.txtOb.setText("Telai OUT : "+ text)
        self.ui.txtOb.setFont(self.font)


    def update_lab(self):
        self.ui.label.setText("Premi Start per iniziare\no\nscegli le opzioni nel Menu")
        custom_font = QFont()
        custom_font.setPointSize(20)
        self.ui.label.setFont(custom_font)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.groupBoxMenu.setEnabled(False) #CAMBIATO PER PROGRAMMA TELAI
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #48c75b;} ")##btnStart:hover{background-color: #ffffff;}
    
    
#richiamo del main
if __name__ == '__main__':

    app = QApplication(sys.argv)    #creazione applicazione grafica
    time.sleep(1)   #aspetto la creazione grafica dell'app

    app.setStyleSheet(Path('style.qss').read_text())    #richiamo al file qss (css di python)
    window = Finestra() #creo l'oggetto finestra
    
    sys.exit(app.exec())    #comando per eseguire la applicazione
