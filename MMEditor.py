#!/usr/bin/env python3
# MMEditor
# Majora's Mask Editor

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
DEFAULT_FILENAME = "Project.mme"

# The UI file for the main window.
UI_FILE = os.path.join("UI", "Main.ui")


class MMEditor(QObject):
    """The Majora's Mask Editor class."""

    def __init__(self):
        """Initializes the application and opens the main window."""

        super().__init__()
        self.ui = QUiLoader().load(UI_FILE)
        self.ui.show()

        # Initialize variables.
        self.currentPath = None
        self.project = None

        # Connect the actions to their respective slots.
        self.ui.actionNew.triggered.connect(self.newProject)
        self.ui.actionOpen.triggered.connect(self.openProject)
        self.ui.actionSave.triggered.connect(self.saveProject)
        self.ui.actionSave_as.triggered.connect(lambda x=1: self.saveProject(x))
        self.ui.actionCompile.triggered.connect(self.compileProject)
        self.ui.actionClose.triggered.connect(self.closeProject)
        self.ui.actionQuit.triggered.connect(QCoreApplication.instance().quit)

        # Connect the file tree signals.
        self.ui.FileTree.currentItemChanged.connect(self.changeSelection)

    def __setattr__(self, name, value):
        """Handles project and file switching."""

        if name == "project":
            if value is None:
                self.ui.setWindowTitle("Majora's Mask Editor")
                self.ui.actionSave.setDisabled(True)
                self.ui.actionSave_as.setDisabled(True)
                self.ui.actionCompile.setDisabled(True)
                self.ui.actionClose.setDisabled(True)
            elif value[1] == "":
                projectName = NEW_PROJECT_NAME
            else:
                projectName = os.path.basename(value[1])
            if value is not None:
                self.ui.setWindowTitle("{} - Majora's Mask Editor".format(
                                       projectName))
                self.ui.actionSave.setEnabled(True)
                self.ui.actionSave_as.setEnabled(True)
                self.ui.actionCompile.setEnabled(True)
                self.ui.actionClose.setEnabled(True)
        super().__setattr__(name, value)

    def newProject(self):
        """Creates a new project from a ROM."""

        c = self.closeProject()
        if not c:
            return
        romPath = QFileDialog.getOpenFileName(self.ui, "Open ROM",
                                              self.currentPath,
                                              "Z64 files (*.z64)")[0]
        if not romPath:
            return
        if self.project:
            self.saveProject()
            self.closeProject()
        project = Project(romPath, True)
        if not project:
            QMessageBox.critical(self.ui, "Error",
                                 "There was an error creating the project.")
            return
        if self.project:
            self.saveProject()
        self.project = [project, ""]
        self.createProjectTree(project)

    def openProject(self):
        """Opens an existing project file."""

        c = self.closeProject()
        if not c:
            return
        projectPath = QFileDialog.getOpenFileName(self.ui, "Open Project",
                                                  self.currentPath,
                                                  "MME Project (*.mme)")[0]
        if not projectPath:
            return
        if self.project and self.project[1] == projectPath:
            return
        elif self.project:
            self.saveProject()
            self.closeProject()
        project = Project(projectPath, False)
        if not project:
            QMessageBox.critical(self, "Error",
                                 "There was an error opening the project.")
            return
        self.project = [project, projectPath]
        self.createProjectTree(project)

    def saveProject(self, force=False):
        """Saves the project to a file."""

        if not self.project:
            return
        if not self.project[1] or force:
            name = DEFAULT_FILENAME
            if self.project[1]:
                name = self.project[1]
            savePath = QFileDialog.getSaveFileName(self.ui, "Save Project File",
                                                 name, "MME Project (*.mme)")[0]
        else:
            savePath = self.project[1]
        if not savePath:
            return
        v = self.project[0].save(savePath)
        if not v:
            QMessageBox.critical(self.ui, "Error",
                                 "There was an error saving the project.")
            return
        self.project[1] = savePath
        self.project = self.project

    def createProjectTree(self, idx):
        """Creates the project tree from its files."""

        for b, f in self.project[0].files.items():
            if f.DISPLAY:
                self.ui.FileTree.addTopLevelItem(f)
        self.ui.FileTree.sortItems(0, Qt.AscendingOrder)

    def compileProject(self):
        """Compiles the project's data to a ROM."""

        if not self.project:
            return
        romPath = QFileDialog.getOpenFileName(self.ui, "Open ROM",
                                              self.currentPath,
                                              "Z64 files (*.z64)")[0]
        if not romPath:
            return
        v = self.project[0].compile(romPath)
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
        if not self.project[0].checkSaved():
            name = os.path.basename(self.project[1])
            if not name:
                name = "your New Project"
            s = QMessageBox.question(self.ui, "Save Project?",
                                     "Do you want to save {}?".format(name),
                                     QMessageBox.Yes, QMessageBox.No)
            if s == QMessageBox.Yes:
                if not self.saveProject():
                    return False
        self.ui.FileTree.clear()
        self.project = None
        return True

    def closeEvent(self, event):
        """Called when closing event sent. Checks if all files were saved."""

        if self.project:
            if not self.closeProject():
                event.ignore()
                return
        event.accept()

    def changeSelection(self, current, previous):
        """Called when the selection in the file tree changes."""

        layout = self.ui.FileArea.layout()
        if layout is not None:
            QWidget().setLayout(layout)
        if current:
            current.displayArea(self.ui.FileArea)

########
# MAIN #
########

if __name__ == "__main__":
    a = QApplication(sys.argv)
    m = MMEditor()
    sys.exit(a.exec_())
