# File
# Contains the base file definition for all files.

import os
import struct

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

from Data import *
from UI import *


class File(QTreeWidgetItem):
    """The base class for all files."""

    DISPLAY = False
    LABEL = "File"
    REQUIRED = None

    def __init__(self, label, data):
        """Initialize the file."""

        # GUI.
        super().__init__()
        self.setText(0, self.__class__.LABEL)

        # Data.
        self.label = label
        self.fileArea = None
        self.rawData = bytearray(data)
        self.saved = False
        self._files = {}

    def getData(self, compiling=False):
        """Returns the data which should be written to the project file."""

        fileData = b""
        if not compiling:
            fileData += bytes(self.label, "ascii")
            fileData += bytes([0])
            fileData += len(self.rawData).to_bytes(4, "big")
        fileData += self.rawData
        return fileData

    def giveFile(self, label, fileObject):
        """Gives this file another required file."""

        self._files[label] = fileObject

    def setUnsaved(self):
        """Sets the file to the "unsaved" state."""

        self.saved = False

    def displayArea(self, fileArea):
        """Sets up the file display area."""

        pass
