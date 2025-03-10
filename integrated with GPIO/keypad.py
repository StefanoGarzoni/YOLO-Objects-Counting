#codice per testierino
from PyQt5 import QtCore, QtGui, QtWidgets

#classe tastierino (form)
class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form") #set nome form
        Form.resize(451, 544) #dimensioni tastierio
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred) #politiche di ridimensionamento tastierino (cerca di rimanere delle sue dimensioni)
        
        #impedisco ridimensionamento manuale tasterino
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())

        Form.setSizePolicy(sizePolicy) #applico politche di ridimensionamento al form
        Form.setMinimumSize(QtCore.QSize(451, 544)) #set dimensioni minime
        Form.setMaximumSize(QtCore.QSize(451, 544)) #set dimensioni massime

        self.txtValore = QtWidgets.QTextEdit(Form) #creo schermo del tastierino
        self.txtValore.setGeometry(QtCore.QRect(10, 80, 431, 81)) #dimensioni schermo tastierino

        #font schermo tastierino
        font = QtGui.QFont()
        font.setPointSize(45)
        self.txtValore.setFont(font)

        self.txtValore.setReadOnly(True) #setto schermo a non modificabile dall'utente
        self.txtValore.setObjectName("txtValore") #set nome

        #layout a griglia per i pulsanti 
        self.gridLayoutWidget = QtWidgets.QWidget(Form) #creazione gridLayout
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 190, 411, 341)) #dimensioni gridLayout
        self.gridLayoutWidget.setObjectName("gridLayoutWidget") #set nome
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget) #aggancio gridLayout 
        self.gridLayout.setContentsMargins(0, 0, 0, 0) #margini layout
        self.gridLayout.setObjectName("gridLayout") #set nome

        #BOTTONI TASTIERINO
        self.btn4 = QtWidgets.QPushButton(self.gridLayoutWidget) #creazione bottone e aggiunta al gridLayout
        self.btn4.setMinimumSize(QtCore.QSize(0, 80)) #set dimensione minima
        #font
        font = QtGui.QFont()
        font.setPointSize(40)
        self.btn4.setFont(font)
        self.btn4.setObjectName("btn4")#set nome
        self.gridLayout.addWidget(self.btn4, 1, 0, 1, 1) #aggancio widget al gridLayout

        #7
        self.btn7 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn7.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.btn7.setFont(font)
        self.btn7.setObjectName("btn7")
        self.gridLayout.addWidget(self.btn7, 2, 0, 1, 1)

        #OK
        self.btnOk = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnOk.setMinimumSize(QtCore.QSize(0, 80))
        self.btnOk.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("img/50_Ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off) #icona bottone Ok
        self.btnOk.setIcon(icon)
        self.btnOk.setIconSize(QtCore.QSize(46, 46))
        self.btnOk.setObjectName("btnOk")
        self.gridLayout.addWidget(self.btnOk, 3, 2, 1, 1)

        #5
        self.btn5 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn5.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.btn5.setFont(font)
        self.btn5.setObjectName("btn5")
        self.gridLayout.addWidget(self.btn5, 1, 1, 1, 1)

        #9
        self.btn9 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn9.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.btn9.setFont(font)
        self.btn9.setObjectName("btn9")
        self.gridLayout.addWidget(self.btn9, 2, 2, 1, 1)

        #8
        self.btn8 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn8.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.btn8.setFont(font)
        self.btn8.setObjectName("btn8")
        self.gridLayout.addWidget(self.btn8, 2, 1, 1, 1)

        #0
        self.btn0 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn0.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.btn0.setFont(font)
        self.btn0.setObjectName("btn0")
        self.gridLayout.addWidget(self.btn0, 3, 1, 1, 1)

        #CANCELLA
        self.btnDel = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnDel.setMinimumSize(QtCore.QSize(0, 80))
        self.btnDel.setText("")
        icon = QtGui.QIcon.fromTheme("edit-clear")
        self.btnDel.setIcon(icon)
        self.btnDel.setIconSize(QtCore.QSize(39, 39))
        self.btnDel.setObjectName("btnDel")
        self.gridLayout.addWidget(self.btnDel, 3, 0, 1, 1)

        #6
        self.btn6 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn6.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.btn6.setFont(font)
        self.btn6.setObjectName("btn6")
        self.gridLayout.addWidget(self.btn6, 1, 2, 1, 1)

        #1
        self.btn1 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn1.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.btn1.setFont(font)
        self.btn1.setObjectName("btn1")
        self.gridLayout.addWidget(self.btn1, 0, 0, 1, 1)

        #2
        self.btn2 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn2.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.btn2.setFont(font)
        self.btn2.setObjectName("btn2")
        self.gridLayout.addWidget(self.btn2, 0, 1, 1, 1)

        #3
        self.btn3 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn3.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.btn3.setFont(font)
        self.btn3.setObjectName("btn3")
        self.gridLayout.addWidget(self.btn3, 0, 2, 1, 1)

        #ESCI
        self.btnClose = QtWidgets.QToolButton(Form)
        self.btnClose.setGeometry(QtCore.QRect(380, 10, 61, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.btnClose.setFont(font)
        icon = QtGui.QIcon.fromTheme("window-close")
        self.btnClose.setIcon(icon)
        self.btnClose.setIconSize(QtCore.QSize(43, 43))
        self.btnClose.setObjectName("btnClose")

        self.retranslateUi(Form) #richiamo funzione sottostante
        QtCore.QMetaObject.connectSlotsByName(Form) #gestione automatica dei segnali (eventi)

    #funzione creata in automatico da pyqt-Designer, setto i titoli e i testi
    #per maggiori informazioni controllare retranslateUi di countingYoloRt.py
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Tastierino"))
        self.txtValore.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:45pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.btn4.setText(_translate("Form", "4"))
        self.btn7.setText(_translate("Form", "7"))
        self.btn5.setText(_translate("Form", "5"))
        self.btn9.setText(_translate("Form", "9"))
        self.btn8.setText(_translate("Form", "8"))
        self.btn0.setText(_translate("Form", "0"))
        self.btn6.setText(_translate("Form", "6"))
        self.btn1.setText(_translate("Form", "1"))
        self.btn2.setText(_translate("Form", "2"))
        self.btn3.setText(_translate("Form", "3"))
        self.btnClose.setText(_translate("Form", "..."))
