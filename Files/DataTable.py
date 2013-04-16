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

# DataTable
# Handles the data table.

from Files.File import *

class DataTable(File):
    """The data table class."""

    DISPLAY = True
    DISPLAY_NAME = "Data Table"
    EXPORT_NAME = "DATA_TABLE.zdata"
    IMPORT = False

    def __init__(self, label, data, parent):
        """Initializes the file."""

        super().__init__(label, data, parent)
        self.songs = {}

    def finishSetup(self):
        """Called when the project has loaded all files."""

        self.songs = self.loadSongs()

    def getRawData(self, form=1):
        """Rebuilds the data before returning it."""

        f = DATA["BLOCKS"]["DATA_TABLE"]

        # Prepare the ocarina songs data.
        for l, s in DATA["SONGS"]["LIST"].items():
            if not s["Playback"]:
                continue
            song = self.songs[l]
            s_start = s["Song"] - f
            s_end = s_start + len(song.songData) + 1
            p_start = s["Playback"] - f
            p_end = p_start + len(song.playbackData)
            self.rawData[s_start] = len(song.songData)
            self.rawData[s_start + 1:s_end] = song.songData
            self.rawData[p_start:p_end] = song.playbackData

        return super().getRawData(form)

    def loadSongs(self):
        """Loads all the ocarina songs and their data."""

        songs = {}
        f = DATA["BLOCKS"]["DATA_TABLE"]
        for l, s in DATA["SONGS"]["LIST"].items():

            if not s["Playback"]:  # TEMP
                continue

            # Get the ocarina song notes data.
            pos = s["Song"] - f
            length = int(self.rawData[pos])
            songData = self.rawData[pos + 1:pos + length + 1]

            # Get the song's playback data.
            start = s["Playback"] - f
            i = start
            while int(self.rawData[i]) != 0:
                i += 8
            end = i
            playbackData = self.rawData[start:end]

            songs[l] = Song(songData, playbackData)
        return songs

    def displayArea(self, fileArea):
        """Sets up the various editors for the data table."""

        self.Tabs = QTabWidget()

        # "Ocarina Songs" tab.
        self.Tab_OcarinaSongs = QWidget()
        self.Tabs.addTab(self.Tab_OcarinaSongs, "Ocarina Songs")

        # Generate the list of songs.
        self.SongList = QComboBox(self.Tab_OcarinaSongs)
        for s in sorted(self.songs):
            song = self.songs[s]
            name = DATA["SONGS"]["LIST"][s]["Name"]
            self.SongList.addItem(name, s)
        self.SongList.activated.connect(self.displaySong)

        # Display the first song.
        self.NotesScroll = QScrollArea(self.Tab_OcarinaSongs)
        self.NotesScroll.setWidgetResizable(True)
        self.NotesScrollContents = self.getSong(0)
        self.NotesScroll.setWidget(self.NotesScrollContents)

        # Display the tabs.
        self.Tabs.setCurrentIndex(0)
        VerticalLayout = QVBoxLayout(self.Tab_OcarinaSongs)
        VerticalLayout.addWidget(self.SongList)
        VerticalLayout.addWidget(self.NotesScroll)
        layout = QHBoxLayout(fileArea)
        layout.addWidget(self.Tabs)

    def getSong(self, idx):
        """Sets up the GUI to display the song's information."""

        if isinstance(idx, int):
            song = self.songs[sorted(self.songs)[idx]]
        else:
            song = self.songs[idx]
        NoteList = QWidget()
        NoteListLayout = QHBoxLayout(NoteList)
        hexAddress = QRegExp("([0-9]|[A-F]|[a-f]){0,4}")
        entries = {}
        for entry in DATA["SONGS"]["PLAYBACK_DATA"]["Entries"]:
            entries[entry["Name"]] = entry["Value"]
        functions = {"Button": self.updateNoteButton,
                     "Length": self.updateNoteLength,
                     "Volume": self.updateNoteVolume,
                     "Pitch": self.updateNotePitch,
                     "Vibrato": self.updateNoteVibrato}

        # Display all the notes.
        num = 1
        for note in song:
            NoteBox = QGroupBox(NoteList)
            NoteBox.setTitle("Note #{}".format(num))
            NoteBox.setFixedWidth(200)
            NoteBox.noteIndex = num - 1
            NoteBoxLayout = QFormLayout(NoteBox)

            # Display all the note's properties.
            i = 0
            for k, v in note.items():
                Label = QLabel(k, NoteBox)
                NoteBoxLayout.setWidget(i, QFormLayout.LabelRole, Label)
                value = entries[k]
                f = functions[k]

                # Should it be displayed as a combo box?
                if isinstance(value, dict):
                    ValueWidget = QComboBox(NoteBox)
                    for val, name in value.items():
                        if val != 0xFF:
                            icon = QIcon(":/images/OcarinaButton_{}.png".format(
                                         name))
                            ValueWidget.addItem(icon, name, val)
                        else:
                            ValueWidget.addItem(name, val)
                    ValueWidget.setCurrentIndex(sorted(value).index(v))
                    ValueWidget.activated.connect(f)

                # Otherwise, it should be displayed as an input field.
                else:
                    ValueWidget = QLineEdit(NoteBox)
                    ValueWidget.setMaxLength(4)
                    ValueWidget.setValidator(QRegExpValidator(hexAddress))
                    ValueWidget.setText(hex(v).split("0x", 1)[1].upper())
                    ValueWidget.textEdited.connect(f)
                NoteBoxLayout.setWidget(i, QFormLayout.FieldRole, ValueWidget)

                i += 1

            # Add the delete button.
            DeleteButton = QPushButton("Delete", NoteBox)
            DeleteButton.clicked.connect(self.deleteNote)
            NoteBoxLayout.addRow(DeleteButton)

            NoteBoxLayout.setVerticalSpacing(20)
            NoteListLayout.addWidget(NoteBox)
            num += 1

        # Enable an add note button if the number of notes is inferior to 8.
        AddButton = QPushButton("+", NoteList)
        BigFont = QFont()
        BigFont.setPointSize(50)
        BigFont.setBold(True)
        BigFont.setWeight(75)
        AddButton.setFont(BigFont)
        AddButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        AddButton.clicked.connect(self.addNote)
        NoteListLayout.addWidget(AddButton)

        return NoteList

    def getCurrentSong(self):
        """Returns the song currently selected."""

        idx = self.SongList.currentIndex()
        return self.songs[self.SongList.itemData(idx)]

    def displaySong(self, value):
        """Displays the specified song."""

        self.NotesScrollContents = self.getSong(value)
        self.NotesScroll.setWidget(self.NotesScrollContents)

    def updateNoteVolume(self, value):
        """Updates the volume setting for a note."""

        try:
            value = int(value, 16)
        except ValueError:
            return
        song = self.getCurrentSong()
        noteIndex = self.sender().parent().noteIndex
        note = song[noteIndex]
        oldValue = note["Volume"]
        note["Volume"] = value
        song[noteIndex] = note
        if oldValue != value:
            self.setSaved(False)

    def updateNoteButton(self, idx):
        """Updates the button setting for a note."""

        ButtonList = self.sender()
        song = self.getCurrentSong()
        noteIndex = ButtonList.parent().noteIndex
        note = song[noteIndex]
        value = ButtonList.itemData(idx)
        oldValue = note["Button"]
        note["Button"] = value
        song[noteIndex] = note
        if oldValue != value:
            self.setSaved(False)

    def updateNoteVibrato(self, value):
        """Updates the vibrato setting for a note."""

        try:
            value = int(value, 16)
        except ValueError:
            return
        song = self.getCurrentSong()
        noteIndex = self.sender().parent().noteIndex
        note = song[noteIndex]
        oldValue = note["Vibrato"]
        note["Vibrato"] = value
        song[noteIndex] = note
        if oldValue != value:
            self.setSaved(False)

    def updateNoteLength(self, value):
        """Updates the length setting for a note."""

        try:
            value = int(value, 16)
        except ValueError:
            return
        song = self.getCurrentSong()
        noteIndex = self.sender().parent().noteIndex
        note = song[noteIndex]
        oldValue = note["Length"]
        note["Length"] = value
        song[noteIndex] = note
        if oldValue != value:
            self.setSaved(False)

    def updateNotePitch(self, value):
        """Updates the pitch setting for a note."""

        try:
            value = int(value, 16)
        except ValueError:
            return
        song = self.getCurrentSong()
        noteIndex = self.sender().parent().noteIndex
        note = song[noteIndex]
        oldValue = note["Pitch"]
        note["Pitch"] = value
        song[noteIndex] = note
        if oldValue != value:
            self.setSaved(False)

    def deleteNote(self):
        """Deletes an existing note."""

        del self.getCurrentSong()[self.sender().parent().noteIndex]
        idx = self.SongList.currentIndex()
        self.displaySong(idx)

    def addNote(self):
        """Adds a new note."""

        song = self.getCurrentSong()
        note = {}
        for p in DATA["SONGS"]["PLAYBACK_DATA"]["Entries"]:
            name = p["Name"]
            if name:
                if isinstance(p["Value"], int):
                    value = p["Value"]
                elif isinstance(p["Value"], dict):
                    value = sorted(p["Value"])[0]
                note[name] = value
        song.append(note)
        idx = self.SongList.currentIndex()
        self.displaySong(idx)

class Song(list):
    """A class to manage an ocarina song's data."""

    def __init__(self, songData, playbackData):
        """Creates a song container."""

        super(dict).__init__()
        self.songData = bytearray(songData)
        self.playbackData = bytearray(playbackData)

        i = 0
        while i < len(self.playbackData):
            note = {}
            for p in DATA["SONGS"]["PLAYBACK_DATA"]["Entries"]:
                name = p["Name"]
                if name:
                    value = int.from_bytes(self.playbackData[i:i + p["Size"]],
                                           "big")
                    note[name] = value
                i += p["Size"]
            self.append(note)

    def __setitem__(self, key, value):
        """Modifies the raw data appropriately."""

        super().__setitem__(key, value)

        # Rebuild the data.
        playbackData = bytearray()
        songData = bytearray()
        for note in self:
            for p in DATA["SONGS"]["PLAYBACK_DATA"]["Entries"]:
                s = p["Size"]
                if p["Name"] in note:
                    v = note[p["Name"]]
                else:
                    v = p["Value"]
                playbackData[len(playbackData):] = v.to_bytes(s, "big")
                if p["Name"] == "Button" and v != 0xFF:
                    n = DATA["SONGS"]["SONG_DATA"]["Notes"][v]
                    songData.append(n)
        self.playbackData = playbackData
        self.songData = songData
