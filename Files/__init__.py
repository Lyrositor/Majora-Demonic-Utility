# Files
# The various file type handlers.

import sys

from Data import *

from Files.DialogText import *

def loadFile(f):
    """Loads the file if MMEditor can handle it."""

    FileClass = None
    start = f[0]
    for block, address in DATA["BLOCKS"].items():
        if address == start:
            if block in DATA["FILES"]:
                fileBlock = block
                FileClass = getattr(sys.modules[__name__], DATA["FILES"][block])
            break
    if not FileClass:
        return None
    try:
        fileObject = FileClass(fileBlock, f[2])
    except AttributeError:
        return None
    return fileObject

def openFile(label, data):
    """Opens a project file."""

    FileClass = getattr(sys.modules[__name__],  DATA["FILES"][label])
    fileObject = FileClass(label, data)
    return fileObject
