# Copyright (C) 2001 - 2019 David Fillmore
#
# This file is part of buffle.
#
# buffle is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# buffle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import iff
import tempfile
import os
import sys
import babel


class rect:
    def __init__(self, data=None):
        if data:
            width = data[:4]
            height = data[4:8]
            self.width = int.from_bytes(width, byteorder='big')
            self.height = int.from_bytes(height, byteorder='big')
        else:
            self.width = 0
            self.height = 0

    def getPalette(self):
        return None

    def setPalette(self, palette):
        pass

    def draw(self, window, x, y):
        pass

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def scale(self, width, height):
        newRect = rect()
        newRect.width = width
        newRect.height = height
        return newRect

currentpalette = [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)]

class InvalidBlorbFile(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidIFhdChunk(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class NoExecChunk(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Blorb:
    def __init__(self, filename, game=None):
        try:
            file = open(filename, 'rb')
            self.data = file.read()
            file.close()
        except:
            raise InvalidBlorbFile("Error opening the Blorb file.")
        x = self.findChunk(b'RIdx')
        x += 8
        
        rescount = int.from_bytes(self.data[x:x+4], byteorder='big')
        x += 4
        self.resindex = {}
        self.resindex[b'Pict'] = {}
        self.resindex[b'Snd '] = {}
        self.resindex[b'Exec'] = {}
        for a in range(rescount):
            usage = self.data[x+(a*12):x+(a*12)+4]
            resnum = int.from_bytes(self.data[x+(a*12)+4:x+(a*12)+8], byteorder='big')
            pos = int.from_bytes(self.data[x+(a*12)+8:x+(a*12)+12], byteorder='big')
            try:
                self.resindex[usage][resnum] = pos
            except:
                self.resindex[usage] = {}
                self.resindex[usage][resnum] = pos
            
        #if game:
        #    valid = self.checkgame(game)
        #    if valid == False:
        #        raise InvalidIFhdChunk("The Blorb file does not match the game.")
        #else:
        #    if self.getExec(0) == False:
        #        raise NoExecChunk("The Blorb file does not contain a game file.")
       
        x = self.findChunk(b'RelN')
        if x == 0:
            self.release = 0
        else:
            x += 8
            self.release = (self.data[x] << 8) + self.data[x+1]

    def checkgame(self, game):
        x = self.findChunk(b'IFhd')
        if x == 0:
            return True
        x += 8
        idRelease = int.from_bytes(self.data[x:x+2], byteorder='big')
        x += 2
        idSerial = self.data[x:x+6]
        x+=6
        idChecksum = int.from_bytes(self.data[x:x+2], byteorder='big')

        x = 2
        gameRelease = int.from_bytes(game[x:x+2], byteorder='big')
        x = 0x12
        gameSerial = game[x:x+6]
        x = 0x1C
        gameChecksum = int.from_bytes(game[x:x+2], byteorder='big')
        if gameRelease == idRelease and gameSerial == idSerial and gameChecksum == idChecksum:
            return True
        return False

    def chunkSize(self, place):
        size = int.from_bytes(self.data[place+4:place+8], byteorder='big')
        return size
       
    def chunkType(self, place):
        type = self.data[place:place+4]
        return type
    
    def getExec(self, execnum):
        try:
            x = self.resindex[b'Exec'][execnum]
        except:
            return False
        size = self.chunkSize(x)
        data = self.data[x+8:x+8+size]
        return data

    def getExecFormat(self, execnum):
        try:
            x = self.resindex[b'Exec'][execnum]
        except:
            return False
        type = self.chunkType(x)
        return type
        
    def getPict(self, picnum):
        try:
            x = self.resindex[b'Pict'][picnum]
        except:
            return False
        size = self.chunkSize(x)
        data = self.data[x+8:x+8+size]
        return data

    def getPictFormat(self, picnum):
        try:
            x = self.resindex[b'Pict'][picnum]
        except:
            return False
        type = self.chunkType(x)
        return type

    def getSnd(self, sndnum):
        try:
            x = self.resindex[b'Snd '][sndnum]
        except:
            return False
        type = self.chunkType(x)
        size = self.chunkSize(x)
        if type == b'FORM':
            data = self.data[x:x+8+size]
        else:
            data = self.data[x+8:x+8+size]
        return data

    def getSndFormat(self, sndnum):
        try:
            x = self.resindex[b'Snd '][sndnum]
        except:
            return False
        type = self.chunkType(x)
        if type == b'FORM':
            return b'AIFF'
        else:
            return type
        
    def getSndType(self, sndnum):
        # AIFF Sounds = effect
        # Ogg Sounds = music
        # mod sounds = music
        # Song Sounds = music (unsupported)
        format = self.getSndFormat(sndnum)
        if format == b'AIFF':
            return 0 # effect
        return 1 # music

    def getWinSizes(self):
        x = self.findChunk(b'Reso')
        if x == 0:
            return None
        resosize = self.chunkSize(x)
        resochunk = self.data[x+8:x+8+resosize]
        x = 0
        px = float(int.from_bytes(resochunk[x:x+4], byteorder='big')) # standard window width
        x += 4
        py = float(int.from_bytes(resochunk[x:x+4], byteorder='big')) # standard window height
        x += 4
        minx = int.from_bytes(resochunk[x:x+4], byteorder='big') # minimum window width
        x += 4
        miny = int.from_bytes(resochunk[x:x+4], byteorder='big') # minimum window height
        x += 4
        maxx = int.from_bytes(resochunk[x:x+4], byteorder='big') # maximum window width
        x += 4
        maxy = int.from_bytes(resochunk[x:x+4], byteorder='big') # maximum window height
        return (px, py, minx, miny, maxx, maxy)


    def getScale(self, picnum, winx, winy):
        scaleData = getScaleData(picnum)

        px, py, minx, miny, maxx, maxy = self.getWinSizes()

   
        ratnum = scaleData['ratnum']
        ratden = scaleData['ratden']
        minnum = scaleData['minnum']
        minden = scaleData['minden']
        maxnum = scaleData['maxnum']
        maxden = scaleData['maxden']

        
 
        stdratio = ratnum / ratden
        if minnum != 0:
            minratio = minnum / minden
        else:
            minratio = .0

        if maxnum != 0:
            maxratio = maxnum / maxden
        else:
            maxratio = .0

        if (winx/px) < (winy/py):
            ERF = winx/px
        else:
            ERF = winy/py
        if (ERF * stdratio < minratio) and (minratio != 0):
            R = minratio
        elif (ERF * stdratio > maxratio) and (maxratio != 0):
            R = maxratio
        else:
            R = ERF * stdratio
        return R

    def getScaleData(self, picnum):
        x = self.findChunk(b'Reso')
        scaleData = {'ratnum':1,
                     'ratden':1,
                     'minnum':1,
                     'minden':1,
                     'maxnum':1,
                     'maxden':1
                    }
        if x == 0:
            return scaleData
        resosize = self.chunkSize(x)
        resochunk = self.data[x+8:x+8+resosize]
        x = 24
        entrydata = resochunk[x:]

        entries = len(entrydata) // 28
        found = False

        for a in range(entries):
            b = a * 28
            entry = entrydata[b:b+28]

            if int.from_bytes(entry[:4], byteorder='big') == picnum:
                found = True
                break
        
        if found == False:
            return scaleData
    
        scaleData['ratnum'] = int.from_bytes(entry[4:8], byteorder='big')
        scaleData['ratden'] = int.from_bytes(entry[8:12], byteorder='big')
        scaleData['minnum'] = int.from_bytes(entry[12:16], byteorder='big')
        scaleData['minden'] = int.from_bytes(entry[16:20], byteorder='big')
        scaleData['maxnum'] = int.from_bytes(entry[20:24], byteorder='big')
        scaleData['maxden'] = int.from_bytes(entry[24:28], byteorder='big')
        return scaleData



    def getPalette(self, picnum, palette):
        global currentpalette
    
        if not palette:
            return None
        palette = palette[:16]
        pos = self.findChunk(b'APal')
        if pos == 0:
            return palette
        csize = self.chunkSize(pos)
        chunk = self.data[pos+8:pos+8+csize]
        numentries = csize // 4
        entries = []
        for a in range(numentries):
            entries.append(int.from_bytes(chunk[4*a:(4*a) + 4], byteorder='big'))

        if picnum in entries:
            return currentpalette
        for a in range(2, len(palette)):
            if palette[a] != (0,0,0):
                currentpalette[a] = palette[a][:]
        return palette            

    def findChunk(self, chunkname):
        id = None
        x = 12
        while (id != chunkname) and (x < len(self.data)):
            id = self.data[x:x+4]
            csize = int.from_bytes(self.data[x+4:x+8], byteorder='big')
            if csize % 2 == 1:
                csize += 1
            if id == chunkname:
                break
            x += csize + 8
        if id != chunkname:
            return False
        #x -= csize + 8
        return x

    def listChunks(self):
        id = None
        x = 12
        chunks = []
        while (x < len(self.data)):
            id = self.data[x:x+4]
            csize = int.from_bytes(self.data[x+4:x+8], byteorder='big')
            c = {}
            c['type'] = id
            c['location'] = x
            c['size'] = csize
            chunks.append(c)
            if csize % 2 == 1:
                csize += 1
            x += csize + 8
        return chunks


    def getMetaData(self):
        resoplace = self.findChunk(b'IFmd')
        if resoplace == False:
            return None
        resosize = self.chunkSize(resoplace)
        metadata = self.data[resoplace+8:resoplace+8+resosize]
        return metadata

    def gettitlepic(self):
        resoplace = self.findChunk(b'Fspc')
        if resoplace == None:
            iFiction = self.getmetadata()
            picnum = babel.getcoverpicture(iFiction)
            if picnum != None:
                pic = getpic(picnum, titlepic=True)
            else:
                pic = None
            return pic
        #rfile.seek(resoplace + 4)
        #resosize = int.from_bytes(rfile.read(4), byteorder='big')
        #if resosize != 4:
        #    return None
        #rfile.seek(resoplace+8)
        #picnum = int.from_bytes(rfile.read(4), byteorder='big')
        #pic = getpic(picnum, titlepic=True)
        return None
