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

# Files
# The various file type handlers.

import sys

from Data import *

from Files.DataTable import *
from Files.TextDialog import *

def loadFile(f, parent):
    """Loads the file if it can be handled."""

    FileClass = None
    start = f[0]
    for block, address in DATA["BLOCKS"].items():
        if address == start:
            if block in DATA["FILES"]:
                fileBlock = block
                FileClass = getattr(sys.modules[__name__],
                                    DATA["FILES"][block]["Type"])
            break
    if not FileClass:
        return None
    try:
        fileObject = FileClass(fileBlock, f[4], parent)
    except AttributeError:
        return None
    return fileObject

def openFile(label, data, parent):
    """Opens a project file."""

    FileClass = getattr(sys.modules[__name__],  DATA["FILES"][label]["Type"])
    fileObject = FileClass(label, data, parent)
    return fileObject
