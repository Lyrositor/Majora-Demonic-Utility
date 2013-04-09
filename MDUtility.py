#!/usr/bin/env python3
# MDUtility
# Majora's Demonic Utility

import os
import sys

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

from Project import *
from UI import *

# The default name for a new project.
NEW_PROJECT_NAME = "New Project"

# The default filename for a new project.
DEFAULT_FILENAME = "Project.mdu"

# The UI file for the main window.
UI_FILE = os.path.join("UI", "Main.ui")


class MDUtility(QObject):
    """The Majora's Demonic Utility class."""

    def __init__(self):
        """Initializes the application and opens the main window."""

        super().__init__()
        self.ui = QUiLoader().load(UI_FILE)
        self.ui.show()

        # Initialize variables.
        self.currentFile = None
        self.currentPath = None
        self.showHidden = False
        self.project = None

        # Connect the actions to their respective slots.
        self.ui.actionNew.triggered.connect(self.newProject)
        self.ui.actionOpen.triggered.connect(self.openProject)
        self.ui.actionSave.triggered.connect(self.saveProject)
        self.ui.actionSave_as.triggered.connect(lambda x=1: self.saveProject(x))
        self.ui.actionCompile.triggered.connect(self.compileProject)
        self.ui.actionExport.triggered.connect(self.exportFile)
        self.ui.actionImport.triggered.connect(self.importFile)
        self.ui.actionShow_Hidden_Files.triggered.connect(self.toggleHidden)
        self.ui.actionClose.triggered.connect(self.closeProject)
        self.ui.actionQuit.triggered.connect(QCoreApplication.instance().quit)

    def loadProject(self, project):
        """Activates or deactivates the project GUI elements."""

        m = self.ui.FileList.model()
        if project is None:
            self.ui.setWindowTitle("Majora's Demonic Utility")
            self.ui.actionSave.setDisabled(True)
            self.ui.actionSave_as.setDisabled(True)
            self.ui.actionCompile.setDisabled(True)
            self.ui.actionExport.setDisabled(True)
            self.ui.actionImport.setDisabled(True)
            self.ui.actionShow_Hidden_Files.setDisabled(True)
            self.ui.actionClose.setDisabled(True)
            if m:
                self.ui.FileList.setModel(None)
                m.deleteLater()
        else:
            if project.savePath == "":
                projectName = NEW_PROJECT_NAME
            else:
                projectName = os.path.basename(project.savePath)
            self.ui.setWindowTitle("{} - Majora's Demonic Utility".format(
                                                               projectName))
            self.ui.actionSave.setEnabled(True)
            self.ui.actionSave_as.setEnabled(True)
            self.ui.actionCompile.setEnabled(True)
            self.ui.actionShow_Hidden_Files.setEnabled(True)
            self.ui.actionClose.setEnabled(True)
            self.ui.FileList.setModel(None)
            if m and m is not project:
                m.deleteLater()
            i = len(project.files) - 1
            for l in reversed(sorted(project.files)):
                f = project.files[l]
                if not f.DISPLAY and not self.showHidden:
                    f.displaying = False
                    project.removeRow(i)
                else:
                    f.displaying = True
                i -= 1
            self.ui.FileList.setModel(project)
            s = self.ui.FileList.selectionModel()
            s.currentChanged.connect(self.changeSelection)
        return project

    def newProject(self):
        """Creates a new project from a ROM."""

        romPath = QFileDialog.getOpenFileName(self.ui, "Open ROM",
                                              self.currentPath,
                                              "Z64 files (*.z64)")[0]
        if not romPath:
            return
        c = self.closeProject()
        if not c:
            return
        self.currentPath = os.path.dirname(romPath)
        project = Project(romPath, True)
        if not project:
            QMessageBox.critical(self.ui, "Error",
                                 "There was an error creating the project.")
            return
        self.project = self.loadProject(project)
        self.setStatus("Created new project...")

    def openProject(self):
        """Opens an existing project file."""

        projectPath = QFileDialog.getOpenFileName(self.ui, "Open Project",
                                                  self.currentPath,
                                                  "MDU Project (*.mdu)")[0]
        if not projectPath:
            return
        c = self.closeProject()
        if not c:
            return
        self.currentPath = os.path.dirname(projectPath)
        project = Project(projectPath)
        if not project:
            QMessageBox.critical(self.ui, "Error",
                                 "There was an error opening the project.")
            return
        self.project = self.loadProject(project)
        self.setStatus("Opened MDU project...")

    def saveProject(self, force=False):
        """Saves the project to a file."""

        if not self.project:
            return True
        if not self.project.savePath or force:
            name = DEFAULT_FILENAME
            if self.project.savePath:
                name = self.project.savePath
            savePath = QFileDialog.getSaveFileName(self.ui, "Save Project File",
                                                 name, "MDU Project (*.mdu)")[0]
        else:
            savePath = self.project.savePath
        if not savePath:
            return False
        v = self.project.save(savePath)
        if not v:
            QMessageBox.critical(self.ui, "Error",
                                 "There was an error saving the project.")
            return False
        self.project = self.loadProject(self.project)
        self.setStatus("Saved MDU project...")
        return True

    def compileProject(self):
        """Compiles the project's data to a ROM."""

        if not self.project:
            return
        romPath = QFileDialog.getOpenFileName(self.ui, "Open ROM",
                                              self.currentPath,
                                              "Z64 files (*.z64)")[0]
        if not romPath:
            return
        self.currentPath = os.path.dirname(romPath)
        v = self.project.compile(romPath)
        if v:
            QMessageBox.information(self.ui, "Success",
                                    "Project successfully compiled to ROM!")
        else:
            QMessageBox.critical(self.ui, "Error",
                                 "There was an error compiling the project.")

    def closeProject(self):
        """Closes the project, saving if required."""

        if not self.project:
            return True
        if not self.project.checkSaved():
            name = os.path.basename(self.project.savePath)
            if not name:
                name = "your New Project"
            s = QMessageBox.question(self.ui, "Save Project?",
                                     "Do you want to save {}?".format(name),
                                     QMessageBox.Yes, QMessageBox.No)
            if s == QMessageBox.Yes:
                if not self.saveProject():
                    return False
        self.currentFile = None
        self.project = self.loadProject(None)
        self.changeSelection()
        return True

    def closeEvent(self, event):
        """Called when closing event sent. Checks if all files were saved."""

        if self.project:
            if not self.closeProject():
                event.ignore()
                return
        event.accept()

    def exportFile(self):
        """Exports the current file into the appropriate format."""

        if self.currentFile:
            self.currentFile.exportFile()

    def importFile(self):
        """Imports data into the current file."""

        if self.currentFile:
            self.currentFile.exportFile()

    def toggleHidden(self):
        """Toggles whether or not hidden files are shown."""

        if not self.project:
            return
        self.showHidden = self.ui.actionShow_Hidden_Files.isChecked()
        self.project = self.loadProject(self.project)

    def changeSelection(self, current=None, previous=None):
        """Called when the selection in the file tree changes."""

        self.ui.CentralWidget.layout().removeWidget(self.ui.FileArea)
        self.ui.FileArea.setParent(None)
        self.ui.FileArea.deleteLater()
        self.ui.FileArea = QWidget()
        self.ui.FileArea.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Expanding)
        self.ui.CentralWidget.layout().addWidget(self.ui.FileArea, 0, 1)
        if current:
            f = self.project.getFile(current.row())
            self.ui.actionExport.setEnabled(True)
            if f.IMPORT:
                self.ui.actionImport.setEnabled(True)
            else:
                self.ui.actionImport.setDisabled(True)
            f.displayArea(self.ui.FileArea)
            self.currentFile = f
        else:
            self.ui.actionExport.setDisabled(True)
            self.ui.actionImport.setDisabled(True)

    def setStatus(self, message, timeout=2000):
        """Sets the status bar's current message."""

        s = self.ui.statusBar()
        s.showMessage(message, timeout)

########
# MAIN #
########

if __name__ == "__main__":
    a = QApplication(sys.argv)
    m = MDUtility()
    sys.exit(a.exec_())
