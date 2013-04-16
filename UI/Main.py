from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1000, 600)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        MainWindow.setFont(font)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.CentralWidget = QtGui.QWidget(MainWindow)
        self.CentralWidget.setObjectName(_fromUtf8("CentralWidget"))
        self.gridLayout = QtGui.QGridLayout(self.CentralWidget)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.FileArea = QtGui.QWidget(self.CentralWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FileArea.sizePolicy().hasHeightForWidth())
        self.FileArea.setSizePolicy(sizePolicy)
        self.FileArea.setObjectName(_fromUtf8("FileArea"))
        self.gridLayout.addWidget(self.FileArea, 0, 1, 1, 1)
        self.FileList = QtGui.QListView(self.CentralWidget)
        self.FileList.setMaximumSize(QtCore.QSize(200, 16777215))
        self.FileList.setObjectName(_fromUtf8("FileList"))
        self.gridLayout.addWidget(self.FileList, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.CentralWidget)
        self.Menu = QtGui.QMenuBar(MainWindow)
        self.Menu.setGeometry(QtCore.QRect(0, 0, 1000, 23))
        self.Menu.setDefaultUp(False)
        self.Menu.setObjectName(_fromUtf8("Menu"))
        self.MenuFile = QtGui.QMenu(self.Menu)
        self.MenuFile.setObjectName(_fromUtf8("MenuFile"))
        self.MenuActions = QtGui.QMenu(self.Menu)
        self.MenuActions.setObjectName(_fromUtf8("MenuActions"))
        self.MenuHelp = QtGui.QMenu(self.Menu)
        self.MenuHelp.setObjectName(_fromUtf8("MenuHelp"))
        self.MenuOptions = QtGui.QMenu(self.Menu)
        self.MenuOptions.setObjectName(_fromUtf8("MenuOptions"))
        MainWindow.setMenuBar(self.Menu)
        self.StatusBar = QtGui.QStatusBar(MainWindow)
        self.StatusBar.setObjectName(_fromUtf8("StatusBar"))
        MainWindow.setStatusBar(self.StatusBar)
        self.ToolBar = QtGui.QToolBar(MainWindow)
        self.ToolBar.setMovable(False)
        self.ToolBar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.ToolBar.setObjectName(_fromUtf8("ToolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.ToolBar)
        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionSave_as = QtGui.QAction(MainWindow)
        self.actionSave_as.setObjectName(_fromUtf8("actionSave_as"))
        self.actionClose = QtGui.QAction(MainWindow)
        self.actionClose.setObjectName(_fromUtf8("actionClose"))
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionCompile = QtGui.QAction(MainWindow)
        self.actionCompile.setObjectName(_fromUtf8("actionCompile"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionExport = QtGui.QAction(MainWindow)
        self.actionExport.setObjectName(_fromUtf8("actionExport"))
        self.actionShow_Hidden_Files = QtGui.QAction(MainWindow)
        self.actionShow_Hidden_Files.setCheckable(True)
        self.actionShow_Hidden_Files.setObjectName(_fromUtf8("actionShow_Hidden_Files"))
        self.actionImport = QtGui.QAction(MainWindow)
        self.actionImport.setObjectName(_fromUtf8("actionImport"))
        self.actionWebsite = QtGui.QAction(MainWindow)
        self.actionWebsite.setObjectName(_fromUtf8("actionWebsite"))
        self.MenuFile.addAction(self.actionNew)
        self.MenuFile.addAction(self.actionOpen)
        self.MenuFile.addSeparator()
        self.MenuFile.addAction(self.actionSave)
        self.MenuFile.addAction(self.actionSave_as)
        self.MenuFile.addSeparator()
        self.MenuFile.addAction(self.actionClose)
        self.MenuFile.addAction(self.actionQuit)
        self.MenuActions.addAction(self.actionCompile)
        self.MenuActions.addSeparator()
        self.MenuActions.addAction(self.actionExport)
        self.MenuActions.addAction(self.actionImport)
        self.MenuHelp.addAction(self.actionAbout)
        self.MenuHelp.addSeparator()
        self.MenuHelp.addAction(self.actionWebsite)
        self.MenuOptions.addAction(self.actionShow_Hidden_Files)
        self.Menu.addAction(self.MenuFile.menuAction())
        self.Menu.addAction(self.MenuActions.menuAction())
        self.Menu.addAction(self.MenuOptions.menuAction())
        self.Menu.addAction(self.MenuHelp.menuAction())
        self.ToolBar.addAction(self.actionNew)
        self.ToolBar.addAction(self.actionOpen)
        self.ToolBar.addAction(self.actionSave)
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.actionCompile)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Majora\'s Demonic Utility", None, QtGui.QApplication.UnicodeUTF8))
        self.MenuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.MenuActions.setTitle(QtGui.QApplication.translate("MainWindow", "Actions", None, QtGui.QApplication.UnicodeUTF8))
        self.MenuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.MenuOptions.setTitle(QtGui.QApplication.translate("MainWindow", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.ToolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew.setText(QtGui.QApplication.translate("MainWindow", "New...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", "Open...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_as.setText(QtGui.QApplication.translate("MainWindow", "Save as...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_as.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClose.setText(QtGui.QApplication.translate("MainWindow", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClose.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+W", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCompile.setText(QtGui.QApplication.translate("MainWindow", "Compile", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCompile.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+R", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExport.setText(QtGui.QApplication.translate("MainWindow", "Export File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExport.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+E", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_Hidden_Files.setText(QtGui.QApplication.translate("MainWindow", "Show Hidden Files", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_Hidden_Files.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+H", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImport.setText(QtGui.QApplication.translate("MainWindow", "Import File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImport.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+I", None, QtGui.QApplication.UnicodeUTF8))
        self.actionWebsite.setText(QtGui.QApplication.translate("MainWindow", "Website", None, QtGui.QApplication.UnicodeUTF8))
