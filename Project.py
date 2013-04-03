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
        projectFiles = {}
        for b, f in self.files.items():
            projectFiles[DATA["BLOCKS"][b]] = f.getRawData(1)
        r.updateFiles(projectFiles)
        r.updateCRCs()
        return r.writeToFile(romFilePath)

    def checkSaved(self):
        """Checks if there are unsaved changes to the project."""

        for b, f in self.files.items():
            if not f.saved:
                return False
        return True

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
