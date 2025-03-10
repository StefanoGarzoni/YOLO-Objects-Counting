#Libraries for Graphic Parts with Counting of 2 Objects Detected
from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtWidgets import QRadioButton

#Main graphic window composition class
class Ui_MainWindow(object):
    def setupMainWindow(self, MainWindow):

        self.file_path="utilityFiles/models.txt"    #path for reading models from file
        self.models={}  #two-dimensional list for storing read models
        self.radioButtons={}    #two-dimensional list for storing model names and radio buttons
        self.n=0    #control variable for auto-selecting the first radio button

        MainWindow.setObjectName("MainWindow")  #main window name
        MainWindow.resize(1024, 600)    #main window dimensions

        #main window font
        font = QtGui.QFont()    
        font.setPointSize(11)
        MainWindow.setFont(font)

        #main window widget (where all sub-component widgets are inserted)
        self.centralwidget = QtWidgets.QWidget(MainWindow)  #creation
        self.centralwidget.setObjectName("centralwidget")   #set name

        #container for video window, buttons and text fields (View)
        self.groupBoxView = QtWidgets.QGroupBox(self.centralwidget) #creation and attachment to central widget
        self.groupBoxView.setGeometry(QtCore.QRect(5, 5, 1010, 520))  #dimensions #510
        self.groupBoxView.setObjectName("groupBoxView") #set name
        
        #font group box view
        font = QtGui.QFont()
        font.setPointSize(20)
        self.groupBoxView.setFont(font)

        #video window (label)
        self.label = QtWidgets.QLabel(self.groupBoxView)    #creation and attachment to groupbox view
        self.label.setGeometry(QtCore.QRect(25, 55, 560, 400)) #dimensions
        self.label.setFrameShape(QtWidgets.QFrame.Box)  #set border as 'box'
        self.label.setFrameShadow(QtWidgets.QFrame.Raised)  #set shadow to border
        self.label.setLineWidth(7)  #border width
        self.label.setMidLineWidth(2)   #midline width between border and shadow
        self.label.setText("")  #set text inside video label (needed at program start)
        self.label.setObjectName("label")   #set name 

        #vertical layout for buttons and text fields (vertical alignment of child widgets) -> 
        # contains a horizontal layout for buttons and a vertical layout for text fields
        self.verticalLayoutWidget = QtWidgets.QWidget(self.groupBoxView)    #creation and attachment to group box
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(600, 55, 380, 390)) #dimensions
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget") #set name

        #vertical layout for text fields
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)  #creation and attachment to parent vertical layout
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)  #set margins
        self.verticalLayout.setObjectName("verticalLayout") #set name

        #horizontal layout for buttons
        self.horizontalLayout = QtWidgets.QHBoxLayout() #creation of horizontal layout
        self.horizontalLayout.setObjectName("horizontalLayout") #set name

        #start button
        self.btnStart = QtWidgets.QPushButton(self.verticalLayoutWidget)    #creation and attachment to main vertical layout
        self.btnStart.setMinimumSize(QtCore.QSize(0, 85))   #set minimum size

        #font start button
        font = QtGui.QFont()
        font.setPointSize(22)
        self.btnStart.setFont(font)

        self.btnStart.setCheckable(False)   #set button as normal button and not check button (like a light switch)
        self.btnStart.setEnabled(False)  #disable button usage (enable in main)
        self.btnStart.setObjectName("btnStart") #set name
        self.horizontalLayout.addWidget(self.btnStart)  #attach to horizontal layout

        #restart button
        self.btnRestart = QtWidgets.QPushButton(self.verticalLayoutWidget)   #creation and attachment to main vertical layout
        self.btnRestart.setEnabled(False)   #disable button usage (enable in main)
        self.btnRestart.setMinimumSize(QtCore.QSize(0, 85)) #set minimum size

        #font restart button
        font = QtGui.QFont()
        font.setPointSize(22)
        self.btnRestart.setFont(font)

        self.btnRestart.setObjectName("btnRestart") #set name
        self.horizontalLayout.addWidget(self.btnRestart)     #attach to horizontal layout

        #stop button
        self.btnStop = QtWidgets.QPushButton(self.verticalLayoutWidget) #creation and attachment to main vertical layout
        self.btnStop.setEnabled(False)   #disable button usage (enable in main)
        self.btnStop.setMinimumSize(QtCore.QSize(0, 85))    #set minimum size
        
        #font stop button
        font = QtGui.QFont()
        font.setPointSize(22)
        self.btnStop.setFont(font)

        self.btnStop.setObjectName("btnStop")   #set name
        self.horizontalLayout.addWidget(self.btnStop)   #attach to horizontal layout

        self.verticalLayout.addLayout(self.horizontalLayout)    #attach horizontal layout to main vertical layout
        
        #text box counted pieces
        self.txtObjIn = QtWidgets.QTextEdit(self.verticalLayoutWidget)  #creation and addition to main vertical layout
        self.txtObjIn.setEnabled(True)  #set text box to 'active'
        self.txtObjIn.setMaximumSize(QtCore.QSize(16777215, 50))    #set maximum size

        #font text box counted pieces
        font = QtGui.QFont()
        font.setPointSize(18)
        self.txtObjIn.setFont(font)

        self.txtObjIn.setReadOnly(True) #set non-editable by user
        self.txtObjIn.setObjectName("txtObjIn") #set name
        self.verticalLayout.addWidget(self.txtObjIn)    #add to child vertical layout

        #text box pieces out
        self.txtObjOut = QtWidgets.QTextEdit(self.verticalLayoutWidget)  #creation and addition to main vertical layout
        self.txtObjOut.setEnabled(True) #set text box to 'active'
        self.txtObjOut.setMaximumSize(QtCore.QSize(16777215, 50))   #set maximum size
        self.txtObjOut.setReadOnly(True)     #set non-editable by user
        self.txtObjOut.setObjectName("txtObjOut")   #set name
        self.verticalLayout.addWidget(self.txtObjOut)   #add to child vertical layout

        #text box processing number
        self.txtLav = QtWidgets.QTextEdit(self.verticalLayoutWidget)     #creation and addition to main vertical layout
        self.txtLav.setEnabled(True)    #set text box to 'active'
        self.txtLav.setMaximumSize(QtCore.QSize(16777215, 51))  #set maximum size
        self.txtLav.setObjectName("txtLav") #set name
        self.verticalLayout.addWidget(self.txtLav)  #add to child vertical layout

        #text box pieces goal
        self.txtOb = QtWidgets.QTextEdit(self.verticalLayoutWidget)  #creation and addition to main vertical layout
        self.txtOb.setEnabled(True) #set text box to 'active'
        self.txtOb.setMaximumSize(QtCore.QSize(16777215, 50))   #set maximum size
        self.txtOb.setReadOnly(True)     #set non-editable by user
        self.txtOb.setObjectName("txtOb")   #set name
        self.verticalLayout.addWidget(self.txtOb)   #add to child vertical layout

        #text box total pieces
        self.txtObjTot = QtWidgets.QTextEdit(self.verticalLayoutWidget)  #creation and addition to main vertical layout
        self.txtObjTot.setEnabled(True) #set text box to 'active'
        self.txtObjTot.setMaximumSize(QtCore.QSize(16777215, 50))   #set maximum size

        #font text box total pieces
        font = QtGui.QFont()
        font.setPointSize(18)
        self.txtObjTot.setFont(font)

        self.txtObjTot.setReadOnly(True)     #set non-editable by user
        self.txtObjTot.setObjectName("txtTot")  #set name
        self.verticalLayout.addWidget(self.txtObjTot)   #add to child vertical layout

        #text box (another type) containing the tag "fenixTek..." etc.
        self.txtTag_2 = QtWidgets.QPlainTextEdit(self.groupBoxView) #creation and addition to groupBox
        self.txtTag_2.setGeometry(QtCore.QRect(25, 475, 480, 250))   #set dimensions

        #font of the tag
        font = QtGui.QFont()
        font.setPointSize(12)
        self.txtTag_2.setFont(font)

        self.txtTag_2.setReadOnly(True) #set non-editable by user
        self.txtTag_2.setObjectName("txtTag_2") #set name

        #GroupBox of the Menu
        self.groupBoxMenu = QtWidgets.QGroupBox(self.centralwidget) #creation and attachment to central widget
        self.groupBoxMenu.setGeometry(QtCore.QRect(5, 5, 1010, 520))  #set dimensions

        #font of the groupBox Menu
        font = QtGui.QFont()
        font.setPointSize(15)
        self.groupBoxMenu.setFont(font)

        self.groupBoxMenu.setObjectName("groupBoxMenu") #set name

        #creation group box to contain models (radio buttons with models)
        self.groupBoxMod = QtWidgets.QGroupBox(self.groupBoxMenu)   #creation and attachment to group box menu
        self.groupBoxMod.setGeometry(QtCore.QRect(25, 65, 560, 400))  #set dimensions

        #font group box models
        font = QtGui.QFont()
        font.setPointSize(20)
        self.groupBoxMod.setFont(font)

        self.groupBoxMod.setObjectName("groupBoxMod")   #set name

        #vertical layout inside the group box models containing the title and another vertical layout containing radio buttons
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.groupBoxMod)   #creation and attachment to group box models
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 50, 500, 280)) #set dimensions
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2") #set name

        #vertical layout containing radio buttons (child)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)  #creation and attachment to parent vertical layout
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)    #set margin size
        self.verticalLayout_2.setObjectName("verticalLayout_2") #set name

        #text box (another type) containing the tag "fenixTek..." etc. (this inside the 'Menu' window)
        self.txtTag = QtWidgets.QPlainTextEdit(self.groupBoxMenu)   #creation and attachment to group box
        self.txtTag.setGeometry(QtCore.QRect(25, 475, 480, 30)) #set dimensions

        #font of the tag
        font = QtGui.QFont()
        font.setPointSize(12)
        self.txtTag.setFont(font)

        self.txtTag.setReadOnly(True)   #set non-editable by user
        self.txtTag.setObjectName("txtTag") #set name

        #vertical layout containing object goal and text field (parent)
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.groupBoxMenu)  #creation and attachment to group box
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(600, 55, 380, 380))   #set dimensions
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3") #set name

        #vertical layout containing text field (child)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)  #creation and attachment to parent
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)    #set margin size
        self.verticalLayout_3.setObjectName("verticalLayout_3") #set name

        #text field for title
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.verticalLayoutWidget_3)  #creation and attachment to parent vertical layout
        self.plainTextEdit.setMaximumSize(QtCore.QSize(16777215, 61))   #set maximum size

        #font of the text field
        font = QtGui.QFont()
        font.setPointSize(20)
        self.plainTextEdit.setFont(font)

        self.plainTextEdit.setReadOnly(True)    #set non-editable by user
        self.plainTextEdit.setObjectName("plainTextEdit")   #set name
        self.verticalLayout_3.addWidget(self.plainTextEdit) #attach to child vertical layout

        #editable text field
        self.txtObPezzi = QtWidgets.QTextEdit(self.verticalLayoutWidget_3)   #creation and attachment to parent vertical layout
        self.txtObPezzi.setMaximumSize(QtCore.QSize(16777215, 61))  #set maximum size

        #font text field
        font = QtGui.QFont()
        font.setPointSize(20)
        self.txtObPezzi.setFont(font)

        self.txtObPezzi.setObjectName("txtObPezzi") #set name
        self.verticalLayout_3.addWidget(self.txtObPezzi)    #attach to child vertical layout


        MainWindow.setCentralWidget(self.centralwidget) #attach the complete central widget with children to the main window

        """
        self.statusbar = QtWidgets.QStatusBar(MainWindow)  
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        """

        #tool bar containing menu and save buttons at the top
        self.toolBar = QtWidgets.QToolBar(MainWindow)   #creation and addition to main window
        self.toolBar.setMinimumSize(QtCore.QSize(0, 57))    #set maximum size

        #font tool bar
        font = QtGui.QFont()
        font.setPointSize(11)
        self.toolBar.setFont(font)

        self.toolBar.setMovable(False)  #set tool bar as 'fixed'
        self.toolBar.setFloatable(False)    #set false the option to extract it from the window as a secondary sub-window
        self.toolBar.setObjectName("toolBar")   #set name
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)   #attach to main window

        self.actionMenu = QtWidgets.QAction(MainWindow) #menu / view button action

        #font of the button
        font = QtGui.QFont()
        font.setPointSize(18)
        self.actionMenu.setFont(font)

        self.actionMenu.setObjectName("actionMenu") #set name
        self.toolBar.addAction(self.actionMenu) #add action to button in tool bar
 
        self.actionSave = QtWidgets.QAction(MainWindow) #save button action

        #font of the button
        font = QtGui.QFont()
        font.setPointSize(18)
        self.actionSave.setFont(font)

        self.actionSave.setObjectName("actionSave") #set name
        self.toolBar.addAction(self.actionSave) #add action to button in tool bar


        self.retranslateUi(MainWindow)  #call function below
        QtCore.QMetaObject.connectSlotsByName(MainWindow)   #automatic signal management (widget events)
        self.read_file()    #call function below

    #function created automatically by pyQT-designer, the following commands perform similar operations for all widgets,
    #setting texts or HTML content inside UI elements.
    #In general, this code is responsible for translating or updating visible texts within the user interface
    #when the retranslateUi method is called. This is useful when you want to make the application multilingual
    #or when you want to allow users to dynamically modify displayed texts.
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
    
    #function to read models.txt file and fill two-dimensional lists
    def read_file(self):
        with open(self.file_path, "r") as file: #read the file
            for line in file:
                parts = line.strip().split(";") #split the lines
                if len(parts) >= 2:
                    chiave = parts[1]
                    valore = parts[0]
                    self.models[chiave] = []    #create a list within the list
                    self.models[chiave].append(valore)  #add a field to the sublist
            
        for chiave,valori in self.models.items():   #scroll through the two-dimensional list and create radio buttons
            if chiave:
                for valore in valori:
                    radioBtn = QRadioButton(chiave)
                    if self.n == 0: #if it's the first radio button, select it automatically
                        radioBtn.setChecked(True)
                    else:
                        radioBtn.setChecked(False)
                    self.n += 1
                    self.radioButtons[valore]=[]    #create a second two-dimensional list [key = model path | value = radio button]
                    self.radioButtons[valore].append(radioBtn)
                    self.verticalLayout_2.addWidget(radioBtn)




