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

# Yaz0
# Yaz0 compression and decompression module.

from . import simpleEnc

M = 0xFFFFFFFF

def decode(src):
    """Returns the Yaz0-decompressed data.
    Source: http://spinout182.com/z-filenew/yaz0/yaz0dec.c"""

    # Check if the file is already decompressed.
    if src[:4] != b"Yaz0":
        return bytearray(src)

    # Keep reading while there are bytes to decompress.
    srcPlace = 16
    dstPlace = 0
    validBitCount = 0
    currCodeByte = 0
    decompressedSize = int.from_bytes(src[4:8], "big") & M
    src = list(src)
    dst = list([0] * decompressedSize)
    while dstPlace < decompressedSize:

        # Read new "code" byte if the current one is used up.
        if not validBitCount:
            currCodeByte = src[srcPlace]
            srcPlace += 1
            validBitCount = 8

        # Is it a straight copy?
        if currCodeByte & 0x80:
            dst[dstPlace] += src[srcPlace]
            dstPlace += 1
            srcPlace += 1

        # Is it an RLE part?
        else:
            byte1 = src[srcPlace]
            byte2 = src[srcPlace + 1]
            srcPlace += 2

            dist = ((byte1 & 0xF) << 8) | byte2
            copySource = dstPlace - (dist + 1)

            numBytes = byte1 >> 4
            if numBytes:
                numBytes += 2
            else:
                numBytes = src[srcPlace] + 0x12
                srcPlace += 1

            # Copy run.
            for i in range(numBytes):
                dst[dstPlace] = dst[copySource]
                copySource += 1
                dstPlace += 1
        
        # Use next bit from "code" byte.
        currCodeByte <<= 1
        validBitCount -= 1

    return bytearray(dst)


class encode:
    """Encodes data in the Yaz0 format.
    Source: http://vg64tools.googlecode.com/svn/pc/z64porter/trunk/yaz0.c"""

    def __init__(self, src):
        """Returns the Yaz0-compressed data."""

        self.matchPos = None
        self.matchPos1 = None
        self.numBytes1 = None
        self.prevFlag = 0
        self.src = src
        self.srcSize = len(self.src)

        # Check if the file is already compressed.
        if self.src[:4] == b"Yaz0":
            self.data = bytearray(self.src)
            return

        # Allocate enough space to write the compressed data; excess space will
        # be trimmed afterwards.
        # In some cases, the compressed size is superior to the source size; the
        # extra 0x20 bytes account for this.
        self.data = list([0] * (self.srcSize + 0x20))
        self.data[:4] = [ord(c) for c in "Yaz0"]  # Yaz0 header.
        self.data[4:8] = self.srcSize.to_bytes(4, "big")  # Size.
        self.data[8:16] = [0] * 8  # Dummy bytes.
        pos = 16

        # Keep reading while there are bytes to compress.
        srcPos = 0
        dstPos = 0
        dst = [0] * 8 * 3
        validBitCount = 0
        currCodeByte = 0
        while srcPos < self.srcSize:
            numBytes = self.nintendoEnc(srcPos)

            # Should it be a straight copy?
            if numBytes < 3:
                dst[dstPos] = self.src[srcPos]
                srcPos += 1
                dstPos += 1
                currCodeByte |= (0x80 >> validBitCount)

            # Should it be an RLE part?
            else:
                dist = srcPos - self.matchPos - 1
                byte1 = byte2 = byte3 = 0

                # Should it be a 3-byte encoding?
                if numBytes >= 0x12:
                    byte1 = 0 | (dist >> 8)
                    byte2 = dist & 0xFF
                    dst[dstPos] = byte1
                    dstPos += 1
                    dst[dstPos] = byte2
                    dstPos += 1
                    if numBytes > 0xFF + 0x12:
                        numBytes = 0xFF + 0x12
                    byte3 = numBytes - 0x12
                    dst[dstPos] = byte3
                    dstPos += 1

                # Should it be a 2-byte encoding?
                else:
                    byte1 = ((numBytes - 2) << 4) | (dist >> 8)
                    byte2 = dist & 0xFF
                    dst[dstPos] = byte1
                    dstPos += 1
                    dst[dstPos] = byte2
                    dstPos += 1

                srcPos += numBytes

            validBitCount += 1

            # Should 8 codes be written?
            if validBitCount == 8:
                self.data[pos] = currCodeByte
                pos += 1
                for i in range(dstPos):
                    self.data[pos] = dst[i]
                    pos += 1

                currCodeByte = validBitCount = dstPos = 0

        if validBitCount > 0:
            self.data[pos] = currCodeByte
            pos += 1
            for i in range(dstPos):
                self.data[pos] = dst[i]
                pos += 1

            currCodeByte = validBitCount = dstPos = 0

        self.data = self.data[:pos]

    def nintendoEnc(self, pos):
        """A look-ahead encoding scheme for ngc Yaz0."""

        numBytes = 1

        # If prevFlag is set, it means that the previous position was determined by
        # look-ahead try, so just use it. This is not the best optimization, but it
        # is Nintendo's choice for speed.
        if self.prevFlag == 1:
            self.matchPos = self.matchPos1
            self.prevFlag = 0
            return self.numBytes1

        self.prevFlag = 0
        numBytes, self.matchPos1 = simpleEnc.encode(self.src, pos)
        self.matchPos = self.matchPos1

        # If this position is RLE-encoded, then compare to copying 1 byte and next
        # position (pos + 1) encoding.
        if numBytes >= 3:
            self.numBytes1, self.matchPos1 = simpleEnc.encode(self.src, pos + 1)
            # If the next position encoding is +2 longer than current position,
            # choose it. This is does not guarantee the best optimization, but
            # fairly good optimization with speed.
            if self.numBytes1 >= numBytes + 2:
                numBytes = 1
                self.prevFlag = 1

        return numBytes

    def simpleEnc(self, pos):
        """Simple and straight encoding scheme for Yaz0."""

        startPos = pos - 0x1000
        numBytes = 1
        matchPos = 0

        if startPos < 0:
            startPos = 0
        for i in range(startPos, pos):
            for j in range(self.srcSize - pos):
                if self.src[i + j] != self.src[j + pos]:
                    break
            if j > numBytes:
                numBytes = j
                matchPos = i
        self.matchPos1 = matchPos
        if numBytes == 2:
            numBytes = 1
        return numBytes

    def getData(self):
        """Returns the encoded data."""

        return bytearray(self.data)
