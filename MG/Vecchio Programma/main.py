#MAIN DEL PROGRAMMA
import sys
from PyQt5.QtWidgets import QWidget, QApplication,QMessageBox
from countingYoloRT11Pollici import Ui_MainWindow
from tastierino import Ui_Form
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import time
from pathlib import Path
from datetime import datetime
import cv2
from ultralytics import YOLO
import supervision as sv
from line_zoneNew import LineZoneNew
import pymssql

import subprocess   #libreria per il riavvio del programma

#libreria per la gestione di un errore nei file di sistema
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

LINE_START = sv.Point(230, 480) #720, 0   |320, 0
LINE_END = sv.Point(230, 0)#720, 1000  |320, 480

#thread contenente il for
class Worker(QObject):   
    #creazione variabili
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
    start = "Lavorazione n. "
    separatore = "------------------------------------------"
    first = 1
    start = True
    nCic=0
    crN=[]
    crC=[]
    ganci=0
    telai=0
    er=0

    server = "192.168.7.226\sqlexpress"
    database = "ScambioVisione"
    username = "visione"
    password = "Visione123!"
    query = "UPDATE tblScambioVisione SET Bilancelle = %d, Telai = %s WHERE IduScambioVisione = 10"
    queryLettura = "SELECT * FROM tblControllo"
    
    #creazione impulsi del thread
    txtObjTotEdit = pyqtSignal(str) #impulso per modificare il campo di testo del totale
    txtObjInEdit = pyqtSignal(str)  #impulso per modificare il campo di testo degli oggetti contati
    txtObjOutEdit = pyqtSignal(str) #impulso per modificare il campo di testo degli oggetti in uscita
    txtLavEdit = pyqtSignal(str)    #impulso per modificare il campo di testo del cambio lavorazione
    pixmapSet = pyqtSignal(QPixmap) #impulso per inviare alla label i frame del video
    stop = pyqtSignal() #impulso per fermare il programma a fine lavorazione
    fineLav = pyqtSignal(str, str)  #impulso per indicare la fine lavorazione (utile per la message box)
    startLav = pyqtSignal() #impulso per segnare che inizia la lavorazione
    write = pyqtSignal()
    
    
    #funzione contenente il FOR della detection Object
    def run(self):
        
        self.line_counter = LineZoneNew(start=LINE_START, end=LINE_END)
        line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=1, text_scale=0.5)
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )
    
        self.model = YOLO(self.modello) 
        if self.er==0:
            self.er=1
            with open("telai.txt", 'r') as file:
                content = file.read()
            self.line_counter.in_count=int(content)
            self.telai=int(content)
            self.total=int(content)
            with open("ganci.txt", 'r') as file:
                content = file.read()
            self.ganci=int(content)


        
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
                
                ris=self.line_counter.trigger(detections=detections)
                line_annotator.annotate(frame=frame, line_counter=self.line_counter)

                
                #adattamento frame immagine a QImage per mostrarlo
                height, width, bytesPerComponent = frame.shape
                bytesPerLine = bytesPerComponent * width
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                image = QImage(frame_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)
                
                for id in ris:
                    if id==-1:
                        continue
                    if id==1:
                        self.telai+=1
                    else :
                        if id==0:
                            self.ganci+=1

                #scrittura su file
                self.write_to_file_gt("ganci.txt", f'{self.ganci}')
                self.write_to_file_gt("telai.txt", f'{self.telai}')

                #query
                conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                cursor = conn.cursor()
                #query = "UPDATE tblScambioVisione SET Bilancelle = %d, Telai = %s WHERE IduScambioVisione = 10" #UPDATE tblScambioVisione SET Bilancelle = %s, Ganci = %s WHERE IduScambioVisione = 10"

                try:
                    cursor.execute(self.query,(self.ganci, str(self.telai)))
                    conn.commit()
                    print("Modifica effettuata con successo!")

                except Exception as e:
                    print(f"Errore durante l'esecuzione della query: {e}")
                    conn.rollback()

                finally:
                    conn.close()

                self.total=self.telai
                #impulsi emessi dal Thread
                self.pixmapSet.emit(QPixmap.fromImage(image))
                self.txtObjTotEdit.emit(str(self.total))
                self.txtObjInEdit.emit(str(self.telai))
                self.txtObjOutEdit.emit(str(self.ganci))
                self.txtLavEdit.emit(str(self.nLav))

                conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                cursor = conn.cursor()
                try:
                    cursor.execute(self.queryLettura)
                    row = cursor.fetchone()
                    value=row[2]
                    if(value==0):
                        break
                except Exception as e:
                    print(f"Errore durante l'esecuzione della query: {e}")
                    conn.rollback()
                
                finally:
                    conn.close()
                
        
                
    #controllo per la funzione STOP
    def setGo(self, b):
        self.go = b
        
    def write_to_file(self, file_path: str, line: str) -> None:
        with open(file_path, "a") as file:
            file.write(line + "\n") 
    
    def write_to_file_gt(self, file_path: str, line: str) -> None:
        with open(file_path, "w") as file:
            file.write(line)

    def createProgram(self, cr):
        print((cr))
            
    def setModel(self, mod, n):
        self.modello = mod
        self.model = YOLO(self.modello)
        if(n!=0):
            self.fineLav.emit("Il programma verrà\nriavviato per apportare\nle modifiche selezionate...", "Cambio Modello")
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Reset")
            msg_box.setText("Cambio oggetto in corso...\nAzzerare il conteggio totale dei pezzi?")
    
            # Personalizza le dimensioni della finestra di dialogo
            msg_box.setStyleSheet("QMessageBox { width: 400px;font-size: 30px; }")
            
            # Personalizza il pulsante "No"
            no_button = msg_box.addButton("No", QMessageBox.NoRole)
            no_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px;}")
    
            # Personalizza il pulsante "Sì"
            yes_button = msg_box.addButton("Sì", QMessageBox.YesRole)
            yes_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px; }")
            
            # Gestisci il click dei pulsanti
            msg_box.exec_()
            if msg_box.clickedButton() == yes_button:
                self.total=0
                self.write.emit()   #salvo le scelte
            # Percorso dello script Bash da eseguire
            script_bash = "utilityFiles/riavvio.sh"
            
            # Esegui lo script Bash
            subprocess.run(["bash", script_bash])
    
        
        
        

#classe di controllo interfaccia grafica
class Finestra(QtWidgets.QMainWindow):
    work = Worker()
    thread = QThread()
    start = "Lavorazione n. "
    enter = "\n"
    font = ""
    separatore = "------------------------------------------"
    tast = None
    cont = True
    
    #costruttore dell'oggetto della classe
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupMainWindow(self)
        
        self.showFullScreen()
        self.work.crN=self.ui.createrValueN
        self.work.crC=self.ui.createrValueC
        
        #connessione degli eventi ai bottoni e widget
        self.ui.btnStart.clicked.connect(self.clickStart)
        self.ui.btnStop.clicked.connect(self.clickStop)
        self.ui.actionMenu.triggered.connect(self.changeWinMenu)
        self.ui.actionSave.triggered.connect(self.saveTot)
        self.ui.txtObPezzi.mousePressEvent = self.tastierino

        #self.ui.groupBoxMenu.setEnabled(False)  #AGGIUNTO PER PROGRAMMA TELAI
        self.ui.groupBoxMenu.setHidden(True) #nasconde la finestra menu
        self.ui.actionSave.setEnabled(False) #disattiva azione salva
        self.ui.groupBoxMenu.setEnabled(False)  #disattiva la finestra menu

        
        self.work.moveToThread(self.thread) #sposta la classe Work in un thread
        
        cont, self.last,self.mod, tot=self.StartRead()  #funzione di lettura delle ultime scelte
        self.work.total=int(tot)    

        self.work.setModel(self.getChecked(),0)
            
        
        self.thread.started.connect(self.work.run)  #connette il thread alla funzione da runnare
        
        #conetto gli impulsi alle loro funzioni
        self.work.txtObjInEdit.connect(self.update_line_in)
        self.work.txtObjOutEdit.connect(self.update_line_out)
        self.work.txtLavEdit.connect(self.update_line_lav)
        self.work.pixmapSet.connect(self.update_pixmap)
        self.work.stop.connect(self.clickStop)
        self.work.fineLav.connect(self.showMsg)
        self.work.txtObjTotEdit.connect(self.update_tot)
        self.work.startLav.connect(self.update_lab) 
        self.work.write.connect(self.write_change_model)
        
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
        
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #a3a8a5;}")
        self.ui.btnStop.setStyleSheet("#btnStop{background-color: #a3a8a5;}")
        self.ui.btnRestart.setStyleSheet("#btnRestart{background-color: #a3a8a5;}")
        
        #testo del caricamento del programma in attesa della connessione alla webcam
        self.ui.label.setText("Caricamento...")
        custom_font = QFont()
        custom_font.setPointSize(20)
        self.ui.label.setFont(custom_font)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        

        self.thread.start() #starto il thread
        time.sleep(4)

        while True:
            if not(self.thread.is_alive()):
                conn = pymssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
                cursor = conn.cursor()
                try:
                    cursor.execute(self.queryLettura)
                    row = cursor.fetchone()
                    value=row[2]
                    if(value==1):
                        script_bash = "utilityFiles/riavvio.sh"
                        subprocess.run(["bash", script_bash])
                        time.sleep(5)
                except Exception as e:
                    print(f"Errore durante l'esecuzione della query: {e}")
                    conn.rollback()
                
                finally:
                    conn.close()

                



        #self.write_to_file("utilityFiles/count.txt", "\nOggetto: "+self.getNomeRadioBtn()+"\n")



    #funzione che gestisce il bottone start  
    def clickStart(self):

        #ATTENZIONE INIZIO AGGIUNTE PER PROGRAMMA TELAI
        self.cont = False #cont false, è solo true per la prima volta
        self.work.go = True #starto la lavorazione
        #setto campo di testo con l'obiettivo
        self.ui.txtOb.setText("Obiettivo pezzi:      /" )#+ str(self.work.x)
        self.ui.txtOb.setFont(self.font)

        #disattivo il menu
        self.ui.groupBoxMenu.setEnabled(False)
        self.ui.btnStart.setEnabled(False)
        self.ui.btnRestart.setEnabled(False)
        self.ui.btnStop.setEnabled(True)
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #a3a8a5;}")
        self.ui.btnStop.setStyleSheet("#btnStop{background-color: #c74c48;} #btnStop:hover{background-color: #ffffff;}")
        self.ui.btnRestart.setStyleSheet("#btnRestart{background-color: #a3a8a5;}")
        #ATTENZIONE FINE AGGIUNTE PER PROGRAMMA TELAI

    #funzione che gestisce il bottone stop
    def clickStop(self):
        #attivo i tasti
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStop.setEnabled(False)
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #48c75b;} #btnStart:hover{background-color: #ffffff;}")
        self.ui.btnStop.setStyleSheet("#btnStop{background-color: #a3a8a5;}")

        self.work.setGo(False) #fermo la lavorazione


    def update_line_in(self, text):
        self.ui.txtObjIn.setText("Numero Telai: " + text)
        self.ui.txtObjIn.setFont(self.font)
        
    def update_tot(self, text):
        self.ui.txtObjTot.setText("Totale Telai: " + text)
        self.ui.txtObjTot.setFont(self.font)
    
    def update_line_out(self, text):
        self.ui.txtObjOut.setText("Numero Ganci: " + text)
        self.ui.txtObjOut.setFont(self.font)
    
    def update_line_lav(self, text):
        self.ui.txtLav.setText("Lavorazione numero: " + text)
        self.ui.txtLav.setFont(self.font)
        
    def update_pixmap(self, image):
        self.ui.label.setText("")
        self.ui.label.setPixmap(image)

    def update_lab(self):
        self.ui.label.setText("Premi Start per iniziare\no\nscegli le opzioni nel Menu")
        custom_font = QFont()
        custom_font.setPointSize(20)
        self.ui.label.setFont(custom_font)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.groupBoxMenu.setEnabled(False) #CAMBIATO PER PROGRAMMA TELAI
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStart.setStyleSheet("#btnStart{background-color: #48c75b;} #btnStart:hover{background-color: #ffffff;}")
        #self.ui.actionSave.setEnabled(True) #attiva il tasto salva
    

    #prende il valore del radio button (modello) selezionato
    def getChecked(self):
        for chiave, valore in self.ui.radioButtons.items():
            if valore[0].isChecked():
                return chiave
    
    def getNomeRadioBtn(self):
        for valori in self.ui.radioButtons.values() :   
            for valore in valori:
                if valore.isChecked() == True:
                    return valore.text()
    
    #setta il giusto radio button (modello) letto dal file delle ultime scelte
    def setCheck(self):
        for chiave, valori in self.ui.radioButtons.items():
            if chiave==self.mod:
                for valore in valori:
                    valore.setChecked(True)
    
    #funzione del tastierino
    def tastierino(self, event):
        #mostra il tastierino e ne gestisce gli eventi
        self.tast.show()
        self.tast.ui.txtValore.setPlainText("")
        self.tast.ui.btnOk.clicked.connect(self.salva)
        self.tast.ui.btnClose.clicked.connect(self.chiudi)
    
    #chiudi tastierino
    def chiudi(self):
        self.ui.actionMenu.setEnabled(True)
        self.ui.groupBoxMenu.setEnabled(True)
        self.tast.close()
    
    #salva scelta immessa dal tastierino
    def salva(self):
        if len(self.tast.ui.txtValore.toPlainText()) > 0 and self.tast.ui.txtValore.toPlainText() != "0":
            self.ui.txtObPezzi.setPlainText(self.tast.ui.txtValore.toPlainText())
        self.tast.close()
        self.ui.groupBoxMenu.setEnabled(True)
        self.ui.actionMenu.setEnabled(True)
    
    #scrive sul file i dati in elaborazione
    def write_to_file(self, file_path: str, line: str) -> None:
        with open(file_path, "a") as file:
            file.write(line + "\n")
    
    #scrive sul file le ultime scelte
    def WriteStartChoose(self, data1, data2, data3):
        try:
            with open("utilityFiles/last.txt", 'w') as file:
                file.write(f"{data1};{data2};{data3}\n")
            print("Scrittura nel file completata.")
        except Exception as e:
            print("Si è verificato un errore durante la scrittura nel file:", e)

    #legge dal file (all'avvio del programma) le ultime scelte      
    def StartRead(self):
        try:
            with open("utilityFiles/last.txt", 'r') as file:
                content = file.read()
                if( len(content.strip()) == 0 ) : #or len(content.strip()) == 1
                    return 1, None, None, None  # Il file è vuoto
                else:
                    data1, data2, data3 = content.strip().split(';')
                    return 0, data1, data2, data3  # Il file contiene dati
        except FileNotFoundError:
            print("File non trovato.")
            return -1, None, None, None  # Codice di errore se il file non esiste o non è accessibile
        except Exception as e:
            print("Si è verificato un errore:", e)
            return -1, None, None, None  # Codice di errore generico
            
    def write_change_model(self):
        self.WriteStartChoose(self.ui.txtObPezzi.toPlainText(),self.getChecked(),self.work.total)   #salvo le scelte
    
    #funzione generica per la message box
    def showMsg(self, txt, title):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(txt)
        msg.setStyleSheet("QLabel{min-width:400px; font-size: 30px; min-height:100px;} QPushButton{ width:100px; height: 50px; font-size: 18px; }")
        msg.exec_()

    #message box creata per il restart (salvare il totale?)
    def show_confirmation_dialog(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Reset")
        msg_box.setText("Salvare i conteggi trovati fin'ora?")

        # Personalizza le dimensioni della finestra di dialogo
        msg_box.setStyleSheet("QMessageBox { width: 400px;font-size: 30px; }")
        
        # Personalizza il pulsante "No"
        no_button = msg_box.addButton("No", QMessageBox.NoRole)
        no_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px;}")

        # Personalizza il pulsante "Sì"
        yes_button = msg_box.addButton("Sì", QMessageBox.YesRole)
        yes_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px; }")
        
        # Gestisci il click dei pulsanti
        msg_box.exec_()
        if msg_box.clickedButton() == yes_button:   #se la scelta è 'si' scrive sul file i dati e passsa a una nuova lavorazione
            self.work.nLav+=1
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            self.write_to_file('utilityFiles/count.txt', f'{self.separatore}{self.enter}{self.start}{self.work.nLav} {dt_string}')
    
    #alert che avverte che il cambio dell'obiettivo a progreamma in corso comporta la fine della lavorazione
    def show_alert_endLav(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Attenzione")
        msg_box.setText("Obiettivo pezzi impostato uguale\nal numero raggiunto nella lavorazione,\nla lavorazione terminerà,\nContinuare? ")

        # Personalizza le dimensioni della finestra di dialogo
        msg_box.setStyleSheet("QMessageBox { width: 400px;font-size: 30px; }")
        
        # Personalizza il pulsante "No"
        no_button = msg_box.addButton("No", QMessageBox.NoRole)
        no_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px;}")

        # Personalizza il pulsante "Sì"
        yes_button = msg_box.addButton("Sì", QMessageBox.YesRole)
        yes_button.setStyleSheet("QPushButton { width: 80px; height: 40px; font-size: 18px; }")

        # Gestisce il click dei pulsanti
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
        
            self.ui.txtOb.setText("Obiettivo pezzi:      /")# + str(self.work.x)
            #self.ui.txtMod.setText("Modello: " + self.work.modello)
            self.ui.txtOb.setFont(self.font)
            #self.ui.txtMod.setFont(self.font)
            self.ui.groupBoxMenu.setEnabled(False)


#classe di creazione tastierino
class Tastierino(QWidget):
    #font = QFont()
    lista = None
    listaInd = None
    
    def __init__(self, parent): #costruttore del tastierino
        super().__init__(parent)
        
        #eventi e gestione
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

    #funzione al click del tastierino
    def btnClick(self, i):
        self.ui.txtValore.setPlainText(self.ui.txtValore.toPlainText() + str(i))

    #funzione al click sul cancella del tastierino 
    def delete(self):
        if len(self.ui.txtValore.toPlainText()) > 0:
            self.ui.txtValore.setPlainText(self.ui.txtValore.toPlainText()[:-1])
    
#richiamo del main
if __name__ == '__main__':

    app = QApplication(sys.argv)    #creazione applicazione grafica
    time.sleep(1)   #aspetto la creazione grafica dell'app

    app.setStyleSheet(Path('style.qss').read_text())    #richiamo al file qss (css di python)
    window = Finestra() #creo l'oggetto finestra
    window.tast = Tastierino(window)    #creo l'oggetto tastierino come figlio di finestra
    
    sys.exit(app.exec())    #comando per eseguire la applicazione
