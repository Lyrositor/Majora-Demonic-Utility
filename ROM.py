# ROM
# Takes care of reading and writing to a Majora's Mask ROM.

from io import BytesIO
from hashlib import md5
import struct

from Data import *
import Yaz0

# The valid Majora's Mask MD5 hex digest.
MM_MD5 = "2a0a8acb61538235bc1094d297fb6556"


class ROM(BytesIO):
    """Manages the ROM's data."""

    SEED = -0X20D90BCA
    CRC_START = 0x1000
    CRC_LENGTH = 0x100000

    def __init__(self, romFilePath):
        """Loads the ROM file's data."""

        BytesIO.__init__(self)
        v = self.readFromFile(romFilePath)
        if not v:
            return None
        if md5(self.getbuffer()).hexdigest() != MM_MD5:
            return None

    def readFromFile(self, romFilePath):
        """Reads a ROM's data."""

        try:
            f = open(romFilePath, "rb")
        except IOError:
            return False
        self.truncate(0)
        self.write(f.read())
        f.close()
        return True

    def getFiles(self, allFiles=False):
        """Returns a list of all usable files in the ROM."""

        self.seek(DATA["BLOCKS"]["FILESYSTEM"] + 0x30)
        files = []
        fileEntry = self.read(16)
        d = self.getvalue()
        while fileEntry != bytes([0] * 16):
            v_start, v_end, p_start, p_end = struct.unpack(">LLLL", fileEntry)
            # Is the file not processable?
            if p_start in [0, 0xFFFFFFFF] and p_end in [0, 0xFFFFFFFF]:
                if allFiles:
                    files.append(None)
                fileEntry = self.read(16)
                continue

            # Is the file decompressed?
            if p_end == 0:
                size = v_end - v_start
            else:
                size = p_end - p_start
            files.append([v_start, v_end, p_start, p_end,
                          d[p_start:p_start + size]])
            fileEntry = self.read(16)
        return files

    def updateFiles(self, projectFiles):
        """Update the ROM data's files."""

        romFiles = self.getFiles(True)
        data = bytearray(self.getvalue())
        i = DATA["BLOCKS"]["FILESYSTEM"] + 0x30
        p_offset = 0
        for f in romFiles:
            if not f:
                i += 16
                continue

            # Load the old file's data.
            v_oldStart, v_oldEnd, p_oldStart, p_oldEnd, oldData = f
            v_oldSize = v_oldEnd - v_oldStart
            p_oldSize = p_oldEnd - p_oldStart

            if f[0] in projectFiles:
                # Load the new file's data.
                projectFile = projectFiles[f[0]]
                newData = projectFile.getRawData()

                # Prepare the file data.
                if len(newData) < v_oldSize:
                    newData += bytes([0] * (v_oldSize - len(newData)))
                v_newSize = len(newData)

                # Compress the data if needed.
                compress = DATA["FILES"][projectFile.label]["Compress"]
                if compress:
                    newData = Yaz0.encode(newData).getData()
                p_newSize = len(newData)
            else:
                v_newSize = v_oldSize
                p_newSize = p_oldSize
                newData = oldData

            # Write the new addresses and data.
            v_newStart = v_oldStart
            v_newEnd = v_oldStart + v_newSize
            p_newStart = p_oldStart + p_offset
            if p_oldEnd not in [0, 0xFFFFFFFF]:
                p_newEnd = p_oldStart + p_offset + p_newSize
            else:
                p_newEnd = p_oldEnd
                p_oldSize = v_oldEnd - v_oldStart
                p_newSize = p_oldSize
            print(hex(v_oldStart), hex(v_oldEnd), hex(p_oldStart), hex(p_oldEnd))
            print(hex(v_newStart), hex(v_newEnd), hex(p_newStart), hex(p_newEnd))
            data[i:i + 16] = struct.pack(">LLLL", v_newStart, v_newEnd,
                                         p_newStart, p_newEnd)
            data[p_newStart:p_newStart + p_oldSize] = newData
            p_offset += p_newSize - p_oldSize

            i += 16
        self.seek(0)
        self.truncate()
        self.write(data)
        return True

    def updateCRCs(self):
        """Updates the ROM data's CRCs."""

        crc1, crc2 = self.calculateCRCs()
        b = self.getbuffer()
        d = DATA["BLOCKS"]
        b[d["CRC1"]:d["CRC1"] + 4] = crc1
        b[d["CRC2"]:d["CRC2"] + 4] = crc2
        del b

    def calculateCRCs(self):
        """Calculates the CRCs for the ROM and returns them as two DWORDs."""

        M = 0xFFFFFFFF
        v = self.getbuffer()
        t1 = t2 = t3 = t4 = t5 = t6 = ROM.SEED & M
        d = r = None
        i = ROM.CRC_START
        while i < ROM.CRC_START + ROM.CRC_LENGTH:
            d = int.from_bytes(v[i:i + 4], "big") & M
            if (t6 + d) & M < t6 & M:
                t4 += 1
            t6 += d
            t3 ^= d
            r = ((d << (d & 0x1F)) | (d >> (32 - (d & 0x1F)))) & M
            t5 += r
            if t2 > d:
                t2 ^= r
            else:
                t2 ^= (t6 ^ d) & M
            a = 0x40 + 0x0710 + (i & 0xFF)
            t1 += int.from_bytes(v[a:a + 4], "big") ^ d
            i += 4
        del v
        crc1 = ((t6 ^ t4 ^ t3) & M).to_bytes(4, "big")
        crc2 = ((t5 ^ t2 ^ t1) & M).to_bytes(4, "big")
        return crc1, crc2

    def writeToFile(self, romFilePath):
        """Writes the data to a ROM file."""

        try:
            f = open(romFilePath, "wb")
        except IOError:
            return False
        f.write(self.getbuffer())
        f.close()
        return True
