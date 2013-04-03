# ROM
# Takes care of reading and writing to a Majora's Mask ROM.

from io import BytesIO

from Data import *


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

    def getFiles(self):
        """Returns a list of all the files in the ROM."""

        self.seek(DATA["BLOCKS"]["FILESYSTEM"] + 0x30)
        files = []
        fileEntry = self.read(16)
        b = self.getbuffer()
        while fileEntry != bytes([0] * 16):
            start = int.from_bytes(fileEntry[:4], "big")
            end = int.from_bytes(fileEntry[4:8], "big")
            files.append([start, end, b[start:end]])
            fileEntry = self.read(16)
        del b
        return files

    def updateFiles(self, projectFiles):
        """Update the ROM data's files."""

        romFiles = self.getFiles()
        data = self.getbuffer()
        i = DATA["BLOCKS"]["FILESYSTEM"] + 0x30
        for f in romFiles:
            if f[0] in projectFiles:
                start = f[0]
                end = f[1]
                oldSize = end - start
                fileData = projectFiles[f[0]]
                if len(fileData) < oldSize:
                    fileData += bytes([0] * (oldSize - len(fileData)))
                newSize = len(fileData)
                data[start:start + newSize] = fileData
                data[i:i + 4] = data[i + 8:i + 12] = start.to_bytes(4, "big")
                data[i + 4: i + 8] = (start + newSize).to_bytes(4, "big")
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
