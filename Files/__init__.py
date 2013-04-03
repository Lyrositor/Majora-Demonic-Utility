# Files
# The various file type handlers.

import sys

from Data import *

from Files.TextDialog import *

def loadFile(f, parent):
    """Loads the file if it can be handled."""

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
        fileObject = FileClass(fileBlock, f[2], parent)
    except AttributeError:
        return None
    return fileObject

def openFile(label, data, parent):
    """Opens a project file."""

    FileClass = getattr(sys.modules[__name__],  DATA["FILES"][label])
    fileObject = FileClass(label, data, parent)
    return fileObject
