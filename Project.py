"""
    Majora's Demonic Utility - all-in-one editor for Majora's Mask.
    Copyright (C) 2013  Lyrositor <gagne.marc@gmail.com>

    This file is part of Majora's Demonic Utility.

    Majora's Demonic Utility is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Majora's Demonic Utility is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Majora's Demonic Utility.  If not, see
    <http://www.gnu.org/licenses/>.
"""

# Project
# Handles the project file (creation, saving, compilation).

from PySide.QtCore import *

from Files import *
from ROM import *

# The header identifying files as MDU project files.
HEADER = b"MDU\0"


class Project(QAbstractListModel):
    """A container for all the project data."""

    def __init__(self, filePath, new=False):
        """Creates a new project or opens an existing one."""

        super().__init__()
        self.files = {}
        if new:
            v = self.create(filePath)
            self.savePath = ""
        else:
            v = self.open(filePath)
            self.savePath = filePath
        if not v:
            return None

    # Project methods.

    def create(self, romFilePath):
        """Creates a new project from a ROM."""

        r = ROM(romFilePath)
        if not r:
            return False
        self.files = {}
        for f in map(lambda x: loadFile(x, self), r.getFiles()):
            if f:
                self.files[f.label] = f
        r.close()
        for b, projectFile in self.files.items():
            projectFile.finishSetup()
        return True

    def open(self, projectFilePath):
        """Opens an exisiting project file."""

        try:
            f = open(projectFilePath, "rb")
        except IOError:
            return False
        if f.read(4) != HEADER:
            return False
        self.files = {}
        while True:
            c = f.read(1)
            if not c:
                break
            label = ""
            while c != b"\0":
                label += str(c, "ascii")
                c = f.read(1)
            size = b""
            while len(size) < 4:
                c = f.read(1)
                size += c
            size = int.from_bytes(size, "big")
            data = f.read(size)
            self.files[label] = openFile(label, data, self)
        f.close()
        for b, projectFile in self.files.items():
            projectFile.finishSetup()
            projectFile.setSaved()
        return True

    def save(self, projectFilePath):
        """Save the project to a file."""

        try:
            f = open(projectFilePath, "wb")
        except IOError:
            return False
        self.beginSave()
        f.write(HEADER)
        for b, projectFile in self.files.items():
            f.write(projectFile.getRawData(0))
            projectFile.setSaved()
        f.close()
        self.savePath = projectFilePath
        return True

    def compile(self, romFilePath):
        """Compiles the project to a ROM."""

        r = ROM(romFilePath)
        if not r:
            return False
        self.beginSave()
        projectFiles = {}
        for b, f in self.files.items():
            projectFiles[DATA["BLOCKS"][b]] = f
        r.updateFiles(projectFiles)
        r.updateCRCs()
        return r.writeToFile(romFilePath)

    def beginSave(self):
        """Informs files that they are being saved."""

        for b, f in self.files.items():
            f.beginSave()

    def checkSaved(self):
        """Checks if there are unsaved changes to the project."""

        return all(f.saved for b, f in self.files.items())

    def getFile(self, index):
        """Gets the file at the specified index."""

        files = [self.files[f] for f in sorted(self.files)
                 if self.files[f].displaying]
        return files[index]

    # QAbstractListModel methods.

    def rowCount(self, parent=QModelIndex()):
        """Returns the number of files."""

        i = 0
        for l, f in self.files.items():
            if f.displaying:
                i += 1
        return i

    def data(self, index, role=Qt.DisplayRole):
        """Returns the file associated with that index."""

        if role == Qt.DisplayRole:
            f = self.getFile(index.row())
            return f.DISPLAY_NAME
        return None
