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

# TextDialog
# Handles dialog text editing.

from copy import deepcopy
import re

from Files.File import *

def FormatHex(intNum):
    """Format a hex number to a control code format."""

    hexNum = hex(intNum).lstrip("0x").upper()
    if not hexNum:
        hexNum = "00"
    elif len(hexNum) == 1:
        hexNum = "0{}".format(hexNum)
    return hexNum

def ReplaceControlCode(matchObj):
    """Replaces a control code with its corresponding bytes."""

    returnBytes = bytearray()
    for group in matchObj.groups()[:-1]:
        if group is None:
            continue
        byteList = group.strip().split()
        for b in byteList:
            returnBytes.append(int(b, 16))
    return returnBytes


class TextDialog(File):
    """The dialog text editor class."""

    DISPLAY = True
    DISPLAY_NAME = "Dialog Text"
    EXPORT_NAME = "DIALOG_TEXT.ztxt"
    EXPORT_TYPE = "Zelda Text Bank (*.ztxt)"
    IMPORT = False

    def __init__(self, label, data, parent):
        """Initializes the file."""

        super().__init__(label, data, parent)
        self.blocks = {}
        self.tableStart = None
        self.tableEnd = None

    def finishSetup(self):
        """Called when the project has loaded all files."""

        project = self.parent()
        f = project.files["DATA_TABLE"]
        self.blocks = self.loadBlocks(f.rawData)

    def beginSave(self):
        """Called when the project is about to be saved/compiled."""

        project = self.parent()
        address = 0
        table = bytearray()
        for b in sorted(self.blocks):
            table += b.to_bytes(2, "big")
            table += bytes([0, 0, 8])
            table += address.to_bytes(3, "big")
            address += len(self.blocks[b].rawData)
        project.files["DATA_TABLE"].rawData[self.tableStart:self.tableEnd] = table
        self.tableEnd = self.tableStart + len(table)

    def getRawData(self, form=1):
        """Rebuilds the data before returning it."""

        data = bytearray()
        for b in sorted(self.blocks):
            data += self.blocks[b].rawData
        self.rawData = data
        self.beginSave()
        return super().getRawData(form)

    def loadBlocks(self, data):
        """Loads the text blocks from the text table."""

        b = DATA["BLOCKS"]
        self.tableStart = b["TEXT_TABLE"] - b["DATA_TABLE"]
        i = self.tableStart
        d = data
        blocks = {}
        while d[i + 2:i + 5] == bytes([0, 0, 8]):
            idx = int.from_bytes(d[i:i + 2], "big")
            address = int.from_bytes(d[i + 5:i + 8], "big")
            blocks[idx] = self.getBlock(address)
            i += 8
        self.tableEnd = i
        return blocks

    def getBlock(self, address):
        """Gets the text block at the specified address."""

        block = TextBlock()
        d = self.rawData
        i = address

        # Get the header.
        header = DATA["TEXT"]["HEADER"]
        a = 0
        for entry in header["Entries"]:
            name = entry["Name"]
            size = entry["Size"]
            value = int.from_bytes(d[i + a:i + a + size], "big")
            block[name] = value
            a += size
        i += header["Size"]

        # Get the text.
        block["Text"] = ""
        while True:
            size = 1
            if d[i] == 0xBF:
                i += size
                break
            if d[i] in range(0x20, 0xB0):
                block["Text"] += chr(d[i])
            else:
                try:
                    c =  DATA["TEXT"]["CONTROL_CODES"][d[i]]
                    if "Size" in c:
                        size = c["Size"]
                    if "Replace" in c:
                        block["Text"] += "{{{}}}".format(c["Replace"])
                    else:
                        code = "[{}".format(FormatHex(d[i]))
                        for a in range(1, size):
                            code += " {}".format(FormatHex(d[i + a]))
                        code += "]"
                        block["Text"] += code
                except KeyError:
                    block["Text"] += "[{}]".format(FormatHex(d[i]))
            i += size

        block.rawData = d[address:i]
        block.fileDataStart = address
        block.fileDataEnd = i
        return block

    def displayArea(self, fileArea):
        """Sets up the dialog text editor's design and logic."""

        d = DATA["TEXT"]["HEADER"]["Entries"]

        # Row 0.
        self.BlockID = QLineEdit()
        self.BlockID.setMaxLength(4)
        hexAddress = QRegExp("([0-9]|[A-F]|[a-f]){0,4}")
        self.BlockID.setValidator(QRegExpValidator(hexAddress))
        self.BlockID.setMaximumWidth(50)
        self.BlockID.setAlignment(Qt.AlignCenter)
        self.PreviousButton = QPushButton()
        self.PreviousButton.setText("<- Previous Block")
        self.NextButton = QPushButton()
        self.NextButton.setText("Next Block ->")

        # Row 1.
        self.CostLabel = QLabel("Cost:")
        self.CostInput = QLineEdit()
        self.CostInput.setAlignment(Qt.AlignHCenter)
        self.CostInput.setMaxLength(4)
        self.CostInput.setValidator(QRegExpValidator(hexAddress))
        self.CostInput.setMaximumWidth(50)
        self.NextBlockLabel = QLabel("Next Block:")
        self.NextBlockInput = QLineEdit()
        self.NextBlockInput.setAlignment(Qt.AlignHCenter)
        self.NextBlockInput.setMaxLength(4)
        self.NextBlockInput.setValidator(QRegExpValidator(hexAddress))
        self.NextBlockInput.setMaximumWidth(50)
        self.IconLabel = QLabel("Icon:")
        self.IconInput = QComboBox()
        for value in sorted(d[2]["Value"]):
            self.IconInput.addItem(d[2]["Value"][value], value)
        self.TypeLabel = QLabel("Box Type:")
        self.TypeInput = QComboBox()
        for value in sorted(d[0]["Value"]):
            self.TypeInput.addItem(d[0]["Value"][value], value)
        self.PositionLabel = QLabel("Position:")
        self.PositionInput = QComboBox()
        for value in sorted(d[1]["Value"]):
            self.PositionInput.addItem(d[1]["Value"][value], value)

        # Row 2.
        self.BlockEdit = QTextEdit()
        self.BlockEdit.setAcceptRichText(False)

        # Row 3.
        self.NewBlockButton = QPushButton("New Block")
        self.DeleteBlockButton = QPushButton("Delete Block")

        # Configure the layout.
        editor = QGridLayout()
        editor.addWidget(self.PreviousButton, 0, 0, Qt.AlignLeft)
        editor.addWidget(self.BlockID, 0, 1, Qt.AlignHCenter)
        editor.addWidget(self.NextButton, 0, 2, Qt.AlignRight)
        toolbar = QHBoxLayout()
        toolbar.addWidget(self.CostLabel)
        toolbar.addWidget(self.CostInput)
        toolbar.addWidget(self.NextBlockLabel)
        toolbar.addWidget(self.NextBlockInput)
        toolbar.addWidget(self.IconLabel)
        toolbar.addWidget(self.IconInput)
        toolbar.addWidget(self.TypeLabel)
        toolbar.addWidget(self.TypeInput)
        toolbar.addWidget(self.PositionLabel)
        toolbar.addWidget(self.PositionInput)
        editor.addLayout(toolbar, 1, 0, 1, 3, Qt.AlignCenter)
        editor.addWidget(self.BlockEdit, 2, 0, 1, 3)
        actions = QHBoxLayout()
        actions.addWidget(self.NewBlockButton)
        actions.addWidget(self.DeleteBlockButton)
        editor.addLayout(actions, 3, 0, 1, 3)
        fileArea.setLayout(editor)

        # Connect the signals.
        self.PreviousButton.clicked.connect(lambda x=0:
                                            self.goToNearbyBlock(-1))
        self.NextButton.clicked.connect(lambda x=0: self.goToNearbyBlock(1))
        self.BlockID.textEdited.connect(self.goToBlock)
        self.CostInput.textEdited.connect(self.updateCost)
        self.NextBlockInput.textEdited.connect(self.updateNextBlock)
        self.IconInput.activated.connect(self.updateIcon)
        self.TypeInput.activated.connect(self.updateType)
        self.PositionInput.activated.connect(self.updatePosition)
        self.BlockEdit.textChanged.connect(self.updateText)
        self.NewBlockButton.clicked.connect(self.createBlock)
        self.DeleteBlockButton.clicked.connect(self.deleteBlock)

        # Load the first block.
        self.goToBlock(sorted(self.blocks)[0])

    def getCurrentBlockID(self):
        """Returns the current block ID."""

        idx = self.BlockID.text()
        try:
            idx = int(idx, 16)
        except ValueError:
            idx = None
        return idx

    def goToNearbyBlock(self, position):
        """Goes to the specified nearby block."""

        if len(self.blocks) <= 1:
            return None
        value = self.getCurrentBlockID()
        if value is None:
            value = 0
        i = value + position
        first = sorted(self.blocks)[0]
        last = sorted(self.blocks)[len(self.blocks) - 1]
        while True:
            try:
                self.blocks[i]
                n = i
                break
            except KeyError:
                if i < 0:
                    n = last
                    break
                elif i > last:
                    n = first
                    break
            i += position
        self.goToBlock(n)
        return True

    def goToBlock(self, idx):
        """Goes to the specified block (by index)."""

        if idx != "" and not isinstance(idx, int):
            idx = int(idx, 16)
        try:
            self.BlockID.setText(hex(idx).split("0x", 1)[1].upper())
            h = DATA["TEXT"]["HEADER"]["Entries"]
            b = self.blocks[idx]
            bCost = hex(b["Cost"]).split("0x", 1)[1].upper()
            bNextBlock = hex(b["Next Block"]).split("0x", 1)[1].upper()
            bIcon = sorted(h[2]["Value"].keys()).index(b["Icon"])
            bType = sorted(h[0]["Value"].keys()).index(b["Type"])
            bPosition = sorted(h[1]["Value"].keys()).index(b["Position"])
            bText = b["Text"]
            self.toggleEditorArea(True)
            self.CostInput.setText(bCost)
            self.NextBlockInput.setText(bNextBlock)
            self.IconInput.setCurrentIndex(bIcon)
            self.TypeInput.setCurrentIndex(bType)
            self.PositionInput.setCurrentIndex(bPosition)
            self.BlockEdit.setPlainText(bText)
        except (KeyError, TypeError, ValueError):
            self.toggleEditorArea(False)
            self.CostInput.clear()
            self.NextBlockInput.clear()
            self.IconInput.setCurrentIndex(-1)
            self.TypeInput.setCurrentIndex(-1)
            self.PositionInput.setCurrentIndex(-1)
            self.BlockEdit.setPlainText("")

    def toggleEditorArea(self, enabled):
        """Toggles all the relevant components of the editor area."""

        self.CostInput.setEnabled(enabled)
        self.NextBlockInput.setEnabled(enabled)
        self.IconInput.setEnabled(enabled)
        self.TypeInput.setEnabled(enabled)
        self.PositionInput.setEnabled(enabled)
        self.BlockEdit.setEnabled(enabled)
        self.DeleteBlockButton.setEnabled(enabled)

    def updateCost(self, value):
        """Updates the block's cost."""

        idx = self.getCurrentBlockID()
        if idx is None or idx not in self.blocks:
            return
        try:
            value = int(value, 16)
        except ValueError:
            return
        oldValue = self.blocks[idx]["Cost"]
        self.blocks[idx]["Cost"] = value
        if oldValue != value:
            self.setSaved(False)

    def updateNextBlock(self, value):
        """Updates the next text block's index."""

        idx = self.getCurrentBlockID()
        if idx is None or idx not in self.blocks:
            return
        try:
            value = int(value, 16)
        except ValueError:
            return
        oldValue = self.blocks[idx]["Next Block"]
        self.blocks[idx]["Next Block"] = value
        if oldValue != value:
            self.setSaved(False)

    def updateIcon(self, value):
        """Updates the block's text box icon."""

        idx = self.getCurrentBlockID()
        if idx is None or idx not in self.blocks or not isinstance(value, int):
            return
        oldValue = self.blocks[idx]["Icon"]
        self.blocks[idx]["Icon"] = self.IconInput.itemData(value)
        if oldValue != value:
            self.setSaved(False)

    def updateType(self, value):
        """Updates the block's text box type."""

        idx = self.getCurrentBlockID()
        if idx is None or idx not in self.blocks or not isinstance(value, int):
            return
        oldValue = self.blocks[idx]["Type"]
        self.blocks[idx]["Type"] = self.TypeInput.itemData(value)
        if oldValue != value:
            self.setSaved(False)

    def updatePosition(self, value):
        """Updates the block's text box position."""

        idx = self.getCurrentBlockID()
        if idx is None or idx not in self.blocks or not isinstance(value, int):
            return
        oldValue = self.blocks[idx]["Position"]
        self.blocks[idx]["Position"] = self.PositionInput.itemData(value)
        if oldValue != value:
            self.setSaved(False)

    def updateText(self):
        """Updates the current block's text."""

        idx = self.getCurrentBlockID()
        if idx is None or idx not in self.blocks:
            return
        oldValue = self.blocks[idx]["Text"]
        self.blocks[idx]["Text"] = self.BlockEdit.toPlainText()
        if oldValue != self.BlockEdit.toPlainText():
            self.setSaved(False)

    def createBlock(self):
        """Creates a new text block, if possible."""

        idx = self.getCurrentBlockID()
        if idx is None or idx == 0xFFFF:
            idx = 0
        if len(self.blocks) <= 0xFFFF:
            try:
                while True:
                    self.blocks[idx]
                    idx += 1
            except KeyError:
                pass
            self.blocks[idx] = TextBlock(True)
            self.goToBlock(idx)
            self.setSaved(False)

    def deleteBlock(self):
        """Deletes the current text block."""

        idx = self.getCurrentBlockID()
        if idx is None or idx not in self.blocks:
            return
        del self.blocks[idx]
        if not self.goToNearbyBlock(-1):
            self.toggleEditorArea(False)
        self.setSaved(False)


class TextBlock(dict):
    """A class to manage a text block's data."""

    def __init__(self, new=False):
        """Creates the empty data container."""

        super(dict).__init__()
        self.rawData = bytearray()
        if new:
            data = bytearray()
            for entry in DATA["TEXT"]["HEADER"]["Entries"]:
                if isinstance(entry["Value"], int):
                    self[entry["Name"]] = entry["Value"]
                    data += entry["Value"].to_bytes(entry["Size"], "big")
                else:
                    value = sorted(entry["Value"])[0]
                    self[entry["Name"]] = value
                    data += value.to_bytes(entry["Size"], "big")
            data += bytes([0xFF] * 4)
            self["Text"] = ""
            self.rawData += data + (0xBF).to_bytes(1, "big")

    def __setitem__(self, key, value):
        """Modifies the raw data appropriately."""

        if self.rawData:
            if key != "Text":
                r = None
                i = 0
                for entry in DATA["TEXT"]["HEADER"]["Entries"]:
                    if entry["Name"] == key:
                        r = [i, i + entry["Size"]]
                        break
                    i += entry["Size"]
                if r:
                    self.rawData[r[0]:r[1]] = value.to_bytes(r[1] - r[0], "big")
            elif key == "Text":
                text = bytearray(value, "ascii")
                codes = DATA["TEXT"]["CONTROL_CODES"]
                for k, v in codes.items():
                    if "Replace" in v:
                        replace = bytes("{{{}}}".format(v["Replace"]), "ascii")
                        text = text.replace(replace, bytes([k]))
                text = re.sub(b"\[([0-9A-Fa-f][0-9A-Fa-f])"
                              b"((\s[0-9A-Fa-f][0-9A-Fa-f])+)?\]",
                              ReplaceControlCode, text)
                r = DATA["TEXT"]["HEADER"]["Size"]
                self.rawData[r:] = bytes(text) + b"\xbf"
        super().__setitem__(key, value)
