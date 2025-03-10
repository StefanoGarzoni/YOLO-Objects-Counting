#librerie parti grafiche
from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtWidgets import QRadioButton

#classe composizione finestra grafica principale
class Ui_MainWindow(object):
    def setupMainWindow(self, MainWindow):

        self.file_path="utilityFiles/models.txt"    #path per la lettura dei modelli da file
        self.models={}  #lista bidimensionale di salvataggio modelli letti
        self.radioButtons={}    #lista bidimensionale di salvataggio nomi modelli e radio buttons
        self.n=0    #variabile di controllo per l'autoselezione del primo radio button

        MainWindow.setObjectName("MainWindow")  #nome finestra grafica principale
        MainWindow.resize(1024, 600)    #dimensioni finestra principale

        #font finestra principale
        font = QtGui.QFont()    
        font.setPointSize(11)
        MainWindow.setFont(font)

        #widget principale della finestra (dove vengono inseriti tutti i sotto componenti widget)
        self.centralwidget = QtWidgets.QWidget(MainWindow)  #creazione
        self.centralwidget.setObjectName("centralwidget")   #set del nome

        #contenitore della finestra video, bottoni e campi di testo (View)
        self.groupBoxView = QtWidgets.QGroupBox(self.centralwidget) #creazione e aggancio al central widget
        self.groupBoxView.setGeometry(QtCore.QRect(5, 5, 1010, 520))  #dimensioni #510
        self.groupBoxView.setObjectName("groupBoxView") #set nome
        
        #font group box view
        font = QtGui.QFont()
        font.setPointSize(20)
        self.groupBoxView.setFont(font)

        #finestra video (label)
        self.label = QtWidgets.QLabel(self.groupBoxView)    #creazione e aggancio alla groupbox view
        self.label.setGeometry(QtCore.QRect(25, 55, 560, 400)) #dimensioni
        self.label.setFrameShape(QtWidgets.QFrame.Box)  #imposta il contorno come 'box'
        self.label.setFrameShadow(QtWidgets.QFrame.Raised)  #imposta l'ombra al contorno
        self.label.setLineWidth(7)  #larghezza contorno
        self.label.setMidLineWidth(2)   #larghezza linea divisoria tra contorno e ombra
        self.label.setText("")  #set testo all'interno della label del video (serve all'inizio del programma)
        self.label.setObjectName("label")   #set nome 

        #vertical layout per bottoni e campi di testo (allineamento verticale dei widget figli) -> 
        # all'interno ha un orizzontal layout per i bottoni e un vertical layout per i campi di testo
        self.verticalLayoutWidget = QtWidgets.QWidget(self.groupBoxView)    #creazione e aggancio alla group box
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(600, 55, 380, 390)) #dimensioni
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget") #set nome

        #vertical layout campi di testo
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)  #creazione e aggancio al vertical layout padre
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)  #impostazioni margini
        self.verticalLayout.setObjectName("verticalLayout") #set nome

        #orizzontal layout per i bottoni
        self.horizontalLayout = QtWidgets.QHBoxLayout() #creazione orizzontal layout
        self.horizontalLayout.setObjectName("horizontalLayout") #set nome

        #bottone start
        self.btnStart = QtWidgets.QPushButton(self.verticalLayoutWidget)    #creazione e aggancio al vertical layout principale
        self.btnStart.setMinimumSize(QtCore.QSize(0, 85))   #imposto la minima dimensione

        #font bottone start
        font = QtGui.QFont()
        font.setPointSize(22)
        self.btnStart.setFont(font)

        self.btnStart.setCheckable(False)   #imposto il bottone a tasto normale e non a check button(tipo tasto della luce)
        self.btnStart.setEnabled(False)  #disattivo la possibilità di usare il bottone (riattivo nel main)
        self.btnStart.setObjectName("btnStart") #set nome
        self.horizontalLayout.addWidget(self.btnStart)  #aggancio all'orizzontal layout

        #bottone restart
        self.btnRestart = QtWidgets.QPushButton(self.verticalLayoutWidget)   #creazione e aggancio al vertical layout principale
        self.btnRestart.setEnabled(False)   #disattivo la possibilità di usare il bottone (riattivo nel main)
        self.btnRestart.setMinimumSize(QtCore.QSize(0, 85)) #imposto la minima dimensione

        #font bottone restart
        font = QtGui.QFont()
        font.setPointSize(22)
        self.btnRestart.setFont(font)

        self.btnRestart.setObjectName("btnRestart") #set nome
        self.horizontalLayout.addWidget(self.btnRestart)     #aggancio all'orizzontal layout

        #bottone stop
        self.btnStop = QtWidgets.QPushButton(self.verticalLayoutWidget) #creazione e aggancio al vertical layout principale
        self.btnStop.setEnabled(False)   #disattivo la possibilità di usare il bottone (riattivo nel main)
        self.btnStop.setMinimumSize(QtCore.QSize(0, 85))    #imposto la minima dimensione
        
        #font bottone stop
        font = QtGui.QFont()
        font.setPointSize(22)
        self.btnStop.setFont(font)

        self.btnStop.setObjectName("btnStop")   #set nome
        self.horizontalLayout.addWidget(self.btnStop)   #aggancio all'orizzontal layout

        self.verticalLayout.addLayout(self.horizontalLayout)    #aggancio l'orizzontal layout al vertical layout principale
        
        #text box pezzi contati
        self.txtObjIn = QtWidgets.QTextEdit(self.verticalLayoutWidget)  #creazione e aggiunta al vertical layout principale
        self.txtObjIn.setEnabled(True)  #imposto la text box su 'attiva'
        self.txtObjIn.setMaximumSize(QtCore.QSize(16777215, 50))    #set dimensioni massime

        #font text box pezzi contati
        font = QtGui.QFont()
        font.setPointSize(18)
        self.txtObjIn.setFont(font)

        self.txtObjIn.setReadOnly(True) #imposto non modificabile dall'utente
        self.txtObjIn.setObjectName("txtObjIn") #set nome
        self.verticalLayout.addWidget(self.txtObjIn)    #lo aggiungo al vertical layout figlio

        #text box pezzi in uscita
        self.txtObjOut = QtWidgets.QTextEdit(self.verticalLayoutWidget)  #creazione e aggiunta al vertical layout principale
        self.txtObjOut.setEnabled(True) #imposto la text box su 'attiva'
        self.txtObjOut.setMaximumSize(QtCore.QSize(16777215, 50))   #set dimensioni massime
        self.txtObjOut.setReadOnly(True)     #imposto non modificabile dall'utente
        self.txtObjOut.setObjectName("txtObjOut")   #set nome
        self.verticalLayout.addWidget(self.txtObjOut)   #lo aggiungo al vertical layout figlio

        #text box numero lavorazione
        self.txtLav = QtWidgets.QTextEdit(self.verticalLayoutWidget)     #creazione e aggiunta al vertical layout principale
        self.txtLav.setEnabled(True)    #imposto la text box su 'attiva'
        self.txtLav.setMaximumSize(QtCore.QSize(16777215, 51))  #set dimensioni massime
        self.txtLav.setObjectName("txtLav") #set nome
        self.verticalLayout.addWidget(self.txtLav)  #lo aggiungo al vertical layout figlio

        #text box obiettivo pezzi
        self.txtOb = QtWidgets.QTextEdit(self.verticalLayoutWidget)  #creazione e aggiunta al vertical layout principale
        self.txtOb.setEnabled(True) #imposto la text box su 'attiva'
        self.txtOb.setMaximumSize(QtCore.QSize(16777215, 50))   #set dimensioni massime
        self.txtOb.setReadOnly(True)     #imposto non modificabile dall'utente
        self.txtOb.setObjectName("txtOb")   #set nome
        self.verticalLayout.addWidget(self.txtOb)   #lo aggiungo al vertical layout figlio

        #text box totale pezzi
        self.txtObjTot = QtWidgets.QTextEdit(self.verticalLayoutWidget)  #creazione e aggiunta al vertical layout principale
        self.txtObjTot.setEnabled(True) #imposto la text box su 'attiva'
        self.txtObjTot.setMaximumSize(QtCore.QSize(16777215, 50))   #set dimensioni massime

        #font text box totale pezzi
        font = QtGui.QFont()
        font.setPointSize(18)
        self.txtObjTot.setFont(font)

        self.txtObjTot.setReadOnly(True)     #imposto non modificabile dall'utente
        self.txtObjTot.setObjectName("txtTot")  #set nome
        self.verticalLayout.addWidget(self.txtObjTot)   #lo aggiungo al vertical layout figlio

        #text box (un'altra tipologia) contenente il tag "fenixTek..." etc.
        self.txtTag_2 = QtWidgets.QPlainTextEdit(self.groupBoxView) #creazione e aggiunta alla groupBox
        self.txtTag_2.setGeometry(QtCore.QRect(25, 475, 480, 250))   #set dimensioni

        #font del tag
        font = QtGui.QFont()
        font.setPointSize(12)
        self.txtTag_2.setFont(font)

        self.txtTag_2.setReadOnly(True) #imposto non modificabile dall'utente
        self.txtTag_2.setObjectName("txtTag_2") #set nome

        #GroupBox del Menu
        self.groupBoxMenu = QtWidgets.QGroupBox(self.centralwidget) #creazione e aggancio al central widget
        self.groupBoxMenu.setGeometry(QtCore.QRect(5, 5, 1010, 520))  #set dimensioni

        #font della groupBox Menu
        font = QtGui.QFont()
        font.setPointSize(15)
        self.groupBoxMenu.setFont(font)

        self.groupBoxMenu.setObjectName("groupBoxMenu") #set nome

        #crezione group box per contenere i modelli (i radio button con i modelli)
        self.groupBoxMod = QtWidgets.QGroupBox(self.groupBoxMenu)   #creazione e aggancio alla group box menu
        self.groupBoxMod.setGeometry(QtCore.QRect(25, 65, 560, 400))  #set dimensioni

        #font group box modelli
        font = QtGui.QFont()
        font.setPointSize(20)
        self.groupBoxMod.setFont(font)

        self.groupBoxMod.setObjectName("groupBoxMod")   #set nome

        #vertical layout all'interno della group box modelli che contiene il titolo e un altro vertical layout che contiene i radio button
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.groupBoxMod)   #creazione e aggancio alla group box modelli
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 50, 500, 280)) #set dimensioni
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2") #set nome

        #vertical layout che contiene i radio button (figlio)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)  #creazione e aggancio al vertical layout padre
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)    #set dimensione margini
        self.verticalLayout_2.setObjectName("verticalLayout_2") #set nome

        #text box (un'altra tipologia) contenente il tag "fenixTek..." etc. (questo all'interno della finestra 'Menu')
        self.txtTag = QtWidgets.QPlainTextEdit(self.groupBoxMenu)   #creazione e aggancio alla group box
        self.txtTag.setGeometry(QtCore.QRect(25, 475, 480, 30)) #set dimensioni

        #font del tag
        font = QtGui.QFont()
        font.setPointSize(12)
        self.txtTag.setFont(font)

        self.txtTag.setReadOnly(True)   #imposto non modificabile dall'utente
        self.txtTag.setObjectName("txtTag") #set nome

        #vertical layout che contiene obiettivo oggetti e campo di testo (padre)
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.groupBoxMenu)  #creazione e aggancio alla group box
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(600, 55, 380, 380))   #set dimensioni
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3") #set nome

        #vertical layout che contiene il campo di testo (figlio)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)  #creazione e aggancio al padre
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)    #set dimensione margini
        self.verticalLayout_3.setObjectName("verticalLayout_3") #set nome

        #campo di testo del titolo
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.verticalLayoutWidget_3)  #creazione e aggancio al vertical layout padre
        self.plainTextEdit.setMaximumSize(QtCore.QSize(16777215, 61))   #set dimensioni massime

        #font del campo di testo
        font = QtGui.QFont()
        font.setPointSize(20)
        self.plainTextEdit.setFont(font)

        self.plainTextEdit.setReadOnly(True)    #lo rendo non modificaile dall'utente
        self.plainTextEdit.setObjectName("plainTextEdit")   #set nome
        self.verticalLayout_3.addWidget(self.plainTextEdit) #lo aggancio al vertical layout figlio

        #campo di testo modificabile
        self.txtObPezzi = QtWidgets.QTextEdit(self.verticalLayoutWidget_3)   #creazione e aggancio al vertical layout padre
        self.txtObPezzi.setMaximumSize(QtCore.QSize(16777215, 61))  #set dimensioni massime

        #font campo di testo
        font = QtGui.QFont()
        font.setPointSize(20)
        self.txtObPezzi.setFont(font)

        self.txtObPezzi.setObjectName("txtObPezzi") #set nome
        self.verticalLayout_3.addWidget(self.txtObPezzi)    #lo aggancio al vertical layout figlio


        MainWindow.setCentralWidget(self.centralwidget) #aggancio il central widget completo dei figli alla finestra principale

        """
        self.statusbar = QtWidgets.QStatusBar(MainWindow)  
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        """

        #tool bar contenete i tasti menu e salva in alto
        self.toolBar = QtWidgets.QToolBar(MainWindow)   #creazione e aggiunta alla main window
        self.toolBar.setMinimumSize(QtCore.QSize(0, 57))    #set dimensioni massime

        #font tool bar
        font = QtGui.QFont()
        font.setPointSize(11)
        self.toolBar.setFont(font)

        self.toolBar.setMovable(False)  #imposto la tool bar come 'fissa'
        self.toolBar.setFloatable(False)    #imposto a false l'opzione di estrarla dalla finestra come una sottofinestra secondaria
        self.toolBar.setObjectName("toolBar")   #set nome
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)   #aggancio alla main window

        self.actionMenu = QtWidgets.QAction(MainWindow) #azione del tasto menu / view

        #font del tasto
        font = QtGui.QFont()
        font.setPointSize(18)
        self.actionMenu.setFont(font)

        self.actionMenu.setObjectName("actionMenu") #set nome
        self.toolBar.addAction(self.actionMenu) #aggiungo l'azione al tasto nella tool bar
 
        self.actionSave = QtWidgets.QAction(MainWindow) #azione del tasto salva

        #font del tasto
        font = QtGui.QFont()
        font.setPointSize(18)
        self.actionSave.setFont(font)

        self.actionSave.setObjectName("actionSave") #set nome
        self.toolBar.addAction(self.actionSave) #aggiungo l'azione al tasto nella tool bar


        self.retranslateUi(MainWindow)  #richiamo funzione sottostante
        QtCore.QMetaObject.connectSlotsByName(MainWindow)   #gestione automatica dei segnali (eventi dei widget)
        self.read_file()    #richiamo funzione sottostante

    #funzione creata in automatico da pyQT-designer, i comandi seguenti eseguono operazioni simili per tutti i widget, impostando testi o
    #contenuti HTML all'interno di elementi dell'interfaccia utente.
    #In generale, questo codice sembra responsabile della traduzione o dell'aggiornamento dei testi visibili all'interno dell'interfaccia 
    #utente dell'applicazione quando è chiamato il metodo retranslateUi. Questo è utile quando si desidera rendere l'applicazione multilingue 
    #o quando si vuole consentire agli utenti di modificare dinamicamente i testi visualizzati.
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CountingYoloRT"))
        self.groupBoxView.setTitle(_translate("MainWindow", "View"))
        self.btnStart.setText(_translate("MainWindow", "Run"))
        self.btnRestart.setText(_translate("MainWindow", "Restart"))
        self.btnStop.setText(_translate("MainWindow", "Stop"))
        self.txtObjIn.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:20pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:24pt;\">Numero Telai: </span></p></body></html>"))
        self.createrValueC=[0,1,0,0,0,1,1,1, 0,1,1,0,0,0,0,1, 0,1,1,1,0,0,1,0, 0,1,1,1,1,0,1,0, 0,1,1,0,1,1,1,1, 0,1,1,0,1,1,1,0, 0,1,1,0,1,0,0,1]
        self.txtObjOut.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:20pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:24pt;\">Numero Ganci:</span></p></body></html>"))
        self.txtLav.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:20pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:24pt;\">Lavorazione numero: </span></p></body></html>"))
        self.createrValueN = [0,1,0,1,0,0,1,1, 0,1,1,1,0,1,0,0, 0,1,1,0,0,1,0,1, 0,1,1,0,0,1,1,0, 0,1,1,0,0,0,0,1, 0,1,1,0,1,1,1,0, 0,1,1,0,1,1,1,1]
        self.txtOb.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:20pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:24pt;\">Obiettivo pezzi:      /</span></p></body></html>"))
        self.txtObjTot.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:20pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:24pt;\">Status:</span></p></body></html>"))
        self.txtTag_2.setPlainText(_translate("MainWindow", "Fenix Tek Srl ®  |  0365 388032  |  All Rights Reserved ™"))
        self.groupBoxMenu.setTitle(_translate("MainWindow", "Menu"))
        self.groupBoxMod.setTitle(_translate("MainWindow", "Seleziona modello:"))

        self.txtTag.setPlainText(_translate("MainWindow", "Fenix Tek Srl ®  |  0365 388032  |  All Rights Reserved ™"))
        self.plainTextEdit.setPlainText(_translate("MainWindow", "Obiettivo pezzi:"))
        self.txtObPezzi.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:30pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">/</p></body></html>"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionMenu.setText(_translate("MainWindow", "Menu"))
        self.actionMenu.setToolTip(_translate("MainWindow", "Cambia Schermata"))
        self.actionSave.setText(_translate("MainWindow", "Salva"))
        self.actionSave.setToolTip(_translate("MainWindow", "Salva e azzera il totale"))
    
    #funzione lettura file modelli.txt e riempimento liste bidimensionali
    def read_file(self):
        with open(self.file_path, "r") as file: #leggo il file
            for line in file:
                parts = line.strip().split(";") #splitto le righe
                if len(parts) >= 2:
                    chiave = parts[1]
                    valore = parts[0]
                    self.models[chiave] = []    #creo una lista nella lista
                    self.models[chiave].append(valore)  #aggiungo un campo nella sottolista
            
        for chiave,valori in self.models.items():   #scorro la lista bidimensionale e creo i radio button
            if chiave:
                for valore in valori:
                    radioBtn = QRadioButton(chiave)
                    if self.n == 0: #se il radio button è il primo lo seleziono in automatico
                        radioBtn.setChecked(True)
                    else:
                        radioBtn.setChecked(False)
                    self.n += 1
                    self.radioButtons[valore]=[]    #creo una seconda lista bidimensionale [chiave = path modello | valore = radio button]
                    self.radioButtons[valore].append(radioBtn)
                    self.verticalLayout_2.addWidget(radioBtn)

                
            

