# Project
# Handles the project file (creation, saving, compilation).

import struct

from Files import *
from ROM import *

# The header identifying files as MME project files.
HEADER = b"MME" + bytes([0])


class Project:
    """A container for all the project data."""

    def __init__(self, filePath, new):
        """Creates a new project or opens an existing one."""

        self.files = {}
        if new:
            v = self.create(filePath)
        else:
            v = self.open(filePath)
        if not v:
            return None

    def create(self, romFilePath):
        """Creates a new project from a ROM."""

        r = ROM(romFilePath)
        if not r:
            return False
        self.files = {}
        for f in map(loadFile, r.getFiles()):
            if f:
                self.files[f.label] = f
        r.close()
        self.giveRequiredFiles()
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
            while c != bytes([0]):
                label += str(c, "ascii")
                c = f.read(1)
            size = b""
            while len(size) < 4:
                c = f.read(1)
                size += c
            size = struct.unpack(">L", size)[0]
            data = f.read(size)
            self.files[label] = openFile(label, data)
        f.close()
        self.giveRequiredFiles()
        for b, projectFile in self.files.items():
            projectFile.saved = True
        return True

    def giveRequiredFiles(self):
        """Gives the required files to each file."""

        for b, f in self.files.items():
            if f.REQUIRED:
                for req in f.REQUIRED:
                    f.giveFile(req, self.files[req])

    def save(self, projectFilePath):
        """Save the project to a file."""

        try:
            f = open(projectFilePath, "wb")
        except IOError:
            return False
        f.write(HEADER)
        for b, projectFile in self.files.items():
            f.write(projectFile.getData())
            projectFile.saved = True
        f.close()
        return True

    def compile(self, romFilePath):
        """Compiles the project to a ROM."""

        r = ROM(romFilePath)
        if not r:
            return False
        projectFiles = {}
        for b, f in self.files.items():
            projectFiles[DATA["BLOCKS"][b]] = f.getData(True)
        r.updateFiles(projectFiles)
        r.updateCRCs()
        return r.writeToFile(romFilePath)

    def checkSaved(self):
        """Checks if there are unsaved changes to the project."""

        for b, f in self.files.items():
            if not f.saved:
                return False
        return True
