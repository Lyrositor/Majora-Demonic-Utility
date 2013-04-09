# File
# Contains the base file definition for all files.

import os
import struct

from PySide.QtCore import *
from PySide.QtGui import *

from Data import *
from UI import *
import Yaz0


class File(QObject):
    """The base class for all files."""

    DISPLAY = False
    EXPORT_NAME = "DATA_{}-{}.zdata"
    EXPORT_TYPE = "Zelda Data File (*.zdata)"
    IMPORT = True

    def __init__(self, label, data, parent):
        """Initialize the file."""

        # GUI.
        super().__init__(parent)
        try:
            self.DISPLAY_NAME = self.__class__.DISPLAY_NAME
        except AttributeError:
            start = DATA["BLOCKS"][label]
            end = DATA["BLOCKS"][label] + len(data)
            self.DISPLAY_NAME = "{} - {}".format(hex(start), hex(end))
            self.EXPORT_NAME = File.EXPORT_NAME.format(hex(start), hex(end))

        # Data.
        self.displaying = self.__class__.DISPLAY
        self.fileArea = None
        self.label = label
        self.rawData = Yaz0.decode(data)
        self.saved = False

    def finishSetup(self):
        """Called when the project has loaded all files."""

        pass

    def beginSave(self):
        """Called when the project is about to be saved/compiled."""

        pass

    def getRawData(self, form=1):
        """Returns the data which should be written to a file."""

        fileData = b""
        if form == 0:
            fileData += bytes(self.label, "ascii")
            fileData += bytes([0])
            fileData += len(self.rawData).to_bytes(4, "big")
        fileData += self.rawData
        return fileData

    def setRawData(self, data):
        """Sets the raw data to a new value."""

        self.rawData = data

    def setSaved(self, saved=True):
        """Sets the file to the "saved" or "unsaved" state."""

        self.saved = saved

    def displayArea(self, fileArea):
        """Sets up the file display area."""

        layout = QHBoxLayout()
        self.exportButton = QPushButton("Export File")
        self.exportButton.setFixedWidth(80)
        self.exportButton.clicked.connect(self.exportFile)
        layout.addWidget(self.exportButton)
        layout.setAlignment(self.exportButton, Qt.AlignCenter)
        self.importButton = QPushButton("Import File")
        self.importButton.setFixedWidth(80)
        self.importButton.clicked.connect(self.importFile)
        layout.addWidget(self.importButton)
        layout.setAlignment(self.importButton, Qt.AlignCenter)
        fileArea.setLayout(layout)

    def exportFile(self):
        """Exports this file's data into the appropriate format."""

        exportPath = QFileDialog.getSaveFileName(None, "Export File",
                                          self.EXPORT_NAME, self.EXPORT_TYPE)[0]
        if not exportPath:
            return
        exportFile = open(exportPath, "wb")
        exportFile.write(self.getRawData())
        exportFile.close()
        fileName = os.path.basename(exportPath)
        QMessageBox.information(QWidget(), "File Exported", "File was "
                                "successfully exported to {}.".format(fileName))

    def importFile(self):
        """Imports file data from a file."""

        importPath = QFileDialog.getOpenFileName(None, "Import File", "",
                                                 self.EXPORT_TYPE)[0]
        if not importPath:
            return
        importFile = open(importPath, "rb")
        newData = importFile.read()
        importFile.close()
        self.setRawData(newData)
        if self.getRawData() != newData:
            self.setSaved(False)
        fileName = os.path.basename(importPath)
        QMessageBox.information(QWidget(), "File Imported", "File was "
                                "successfully imported from "
                                "{}.".format(fileName))
