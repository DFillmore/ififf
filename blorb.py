# Copyright (C) 2001 - 2024 David Fillmore
#
# This file is part of ififf.
#
# ififf is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ififf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
from __future__ import annotations

import tempfile
import os
import sys

from . import iff
from . import babel
from .ifchunks import game_identifier_chunk


class resource:
    def __repr__(self):
        return self.usage + ' resource number ' + str(self.number) + ' at ' + str(self.location)

    def __init__(self, usage, number, location):
        self.usage = usage
        self.number = number
        self.location = location


class game:
    number = None
    type = None
    title = None
    author = None
    description = None
    data = b''


class image:
    number = None
    type = None
    data = b''
    standard_numerator = 1
    standard_denominator = 1
    minimum_numerator = 0
    minimum_denominator = 0
    maximum_numerator = 0
    maximum_denominator = 0

    def __init__(self, pic_chunk, number):
        self.type = pic_chunk.ID.strip()
        self.data = pic_chunk.data
        self.number = number


class sound:
    number = None
    type = None
    data = b''
    loop = None

    def __init__(self, snd_chunk, number):
        self.type = snd_chunk.ID.decode('ascii').strip()
        self.data = snd_chunk.data
        self.number = number


class screen:
    standard_width: int = 1
    standard_height: int = 1
    minimum_width: int = 1
    minimum_height: int = 1
    maximum_width: int = 1
    maximum_height: int = 1


class blorb_chunk(iff.form_chunk):
    subID = 'IFRS'


class resource_index_chunk(iff.chunk):
    ID = 'RIdx'

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.resource_count = int.from_bytes(self.raw_data[8:12], byteorder='big')
        self.resources = {}
        for r in range(self.resource_count):
            usage = self.raw_data[12 + r * 12:16 + r * 12].decode('ascii')
            resource_number = int.from_bytes(self.raw_data[16 + r * 12:20 + r * 12], byteorder='big')
            location = int.from_bytes(self.raw_data[20 + r * 12:24 + r * 12], byteorder='big')
            res = resource(usage, resource_number, location)
            try:
                self.resources[usage]
            except:
                self.resources[usage] = []
            self.resources[usage].append(res)

    def create_data(self):
        pass


# Picture Resource Chunks

class png_chunk(iff.chunk):
    ID = 'PNG '


class jpeg_chunk(iff.chunk):
    ID = 'JPEG'


class rect_chunk(iff.chunk):
    ID = 'Rect'

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.width = int.from_bytes(self.raw_data[8:12], byteorder='big')
        self.height = int.from_bytes(self.raw_data[12:16], byteorder='big')

    def create_data(self):
        self.raw_data = self.ID.encode() + self.length.to_bytes(4, 'big') + self.width.to_bytes(4,
                                                                                                'big') + self.height.to_bytes(
            4, 'big')


# Sound Resource Chunks

class aiff_chunk(iff.form_chunk):
    subID = 'AIFF'


class oggv_chunk(iff.chunk):
    ID = 'OGGV'


class mod_chunk(iff.chunk):
    ID = 'MOD '


class song_chunk(iff.chunk):
    ID = 'SONG'


# Data Resource Chunks

class text_data_chunk(iff.chunk):
    ID = 'TEXT'


class binary_data_chunk(iff.chunk):
    ID = 'BINA'


# Executable Resource Chunks

class zcode_chunk(iff.chunk):
    ID = 'ZCOD'


class glulx_chunk(iff.chunk):
    ID = 'GLUL'


class tads2_chunk(iff.chunk):
    ID = 'TAD2'


class tads3_chunk(iff.chunk):
    ID = 'TAD3'


class hugo_chunk(iff.chunk):
    ID = 'HUGO'


class alan_chunk(iff.chunk):
    ID = 'ALAN'


class adri_chunk(iff.chunk):
    ID = 'ADRI'


class level9_chunk(iff.chunk):
    ID = 'LEVE'


class agt_chunk(iff.chunk):
    ID = 'AGT '


class magnetic_scrolls_chunk(iff.chunk):
    ID = 'MAGS'


class advsys_chunk(iff.chunk):
    ID = 'ADVS'


class native_executable_chunk(iff.chunk):
    ID = 'EXEC'


class color_palette_chunk(iff.chunk):
    ID = 'Plte'

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        if self.length == 1:
            self.palette = int.from_bytes(self.raw_data[8], byteorder='big')
        else:
            self.palette = []
            colours = self.length // 3
            for c in range(colours):
                colour = {}
                colour['red'] = int.from_bytes(self.raw_data[8 + c * 3], byteorder='big')
                colour['green'] = int.from_bytes(self.raw_data[9 + c * 3], byteorder='big')
                colour['blue'] = int.from_bytes(self.raw_data[10 + c * 3], byteorder='big')
                colours.append(colour)

    def create_data(self):
        pass


class frontispiece_chunk(iff.chunk):
    ID = 'Fspc'

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.picture_number = int.from_bytes(self.raw_data[8:12], byteorder='big')

    def create_data(self):
        pass


class resource_description_chunk(iff.chunk):
    ID = 'RDes'

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        entries_count = int.from_bytes(self.raw_data[8:12], byteorder='big')
        self.entries = {}
        while p < self.length:
            usage = int.from_bytes(self.raw_data[12 + p:16 + p], byteorder='big')
            try:
                self.entries[usage]
            except:
                self.entries[usage] = {}
            number = int.from_bytes(self.raw_data[16 + p:20 + p], byteorder='big')
            length = int.from_bytes(self.raw_data[20 + p:24 + p], byteorder='big')
            text = self.raw_data[24 + d:24 + p + length].decode('utf-8')
            self.entries[usage][number] = text
            p += 24 + length

    def create_data(self):
        pass


class metadata_chunk(iff.chunk):
    ID = 'IFmd'

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.xml = self.raw_data[8:8 + self.length].decode('utf-8')

    def create_data(self):
        pass


# z-machine chunks

class release_number_chunk(iff.chunk):
    ID = 'RelN'

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.number = int.from_bytes(self.raw_data[8:10], byteorder='big')

    def create_data(self):
        pass


class resolution_chunk(iff.chunk):
    ID = 'Reso'

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.screen = {}
        self.screen['standard_width'] = int.from_bytes(self.raw_data[8:12], byteorder='big')
        self.screen['standard_height'] = int.from_bytes(self.raw_data[12:16], byteorder='big')
        self.screen['minimum_width'] = int.from_bytes(self.raw_data[16:20], byteorder='big')
        self.screen['minimum_height'] = int.from_bytes(self.raw_data[20:24], byteorder='big')
        self.screen['maximum_width'] = int.from_bytes(self.raw_data[24:28], byteorder='big')
        self.screen['maximum_height'] = int.from_bytes(self.raw_data[28:32], byteorder='big')

        self.images = {}
        resolutions_count = (self.length - 24) // 28

        for r in range(resolutions_count):
            image_number = int.from_bytes(self.raw_data[32 + r * 28:36 + r * 28], byteorder='big')
            self.images[image_number] = {}
            self.images[image_number]['standard_numerator'] = int.from_bytes(self.raw_data[36 + r * 28:40 + r * 28],
                                                                             byteorder='big')
            self.images[image_number]['standard_denominator'] = int.from_bytes(self.raw_data[40 + r * 28:44 + r * 28],
                                                                               byteorder='big')
            self.images[image_number]['minimum_numerator'] = int.from_bytes(self.raw_data[44 + r * 28:48 + r * 28],
                                                                            byteorder='big')
            self.images[image_number]['minimum_denominator'] = int.from_bytes(self.raw_data[52 + r * 28:56 + r * 28],
                                                                              byteorder='big')
            self.images[image_number]['maximum_numerator'] = int.from_bytes(self.raw_data[56 + r * 28:60 + r * 28],
                                                                            byteorder='big')
            self.images[image_number]['maximum_denominator'] = int.from_bytes(self.raw_data[60 + r * 28:64 + r * 28],
                                                                              byteorder='big')

    def create_data(self):
        pass


class adaptive_palette_chunk(iff.chunk):
    ID = 'APal'

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        palette_count = self.length // 4
        self.pictures = []
        for p in range(palette_count):
            picture_number = int.from_bytes(self.raw_data[8 + p * 4:12 + p * 4], byteorder='big')
            self.pictures.append(picture_number)

    def create_data(self):
        pass


class looping_chunk(iff.chunk):
    ID = 'Loop'
    sound_looping_data = {}

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        loop_data_count = self.length // 8
        for a in range(loop_data_count):
            sound_number = int.from_bytes(self.raw_data[8 + a * 8:12 + a * 8], byteorder='big')
            repeats = int.from_bytes(self.raw_data[8 + a * 8:12 + a * 8], byteorder='big')
            self.sound_looping_data[sound_number] = repeats

    def create_data(self):
        pass


#

class story_name_chunk(iff.chunk):
    ID = 'SNam'

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.story_name = self.raw_data[8:8 + self.length].decode('utf-16')

    def create_data(self):
        self.raw_data = self.ID.encode() + self.length.to_bytes(4, 'big') + self.story_name.encode()


# adrift

class gif_chunk(iff.chunk):
    ID = 'GIF '


class wav_chunk(iff.chunk):
    ID = 'WAV '


class midi_chunk(iff.chunk):
    ID = 'MIDI'


class mp3_chunk(iff.chunk):
    ID = 'MP3 '


###

chunk_types = {'RIdx': resource_index_chunk,
               'PNG ': png_chunk,
               'JPEG': jpeg_chunk,
               'Rect': rect_chunk,
               'OGGV': oggv_chunk,
               'MOD ': mod_chunk,
               'SONG': song_chunk,
               'TEXT': text_data_chunk,
               'BINA': binary_data_chunk,
               'ZCOD': zcode_chunk,
               'GLUL': glulx_chunk,
               'TAD2': tads2_chunk,
               'TAD3': tads3_chunk,
               'HUGO': hugo_chunk,
               'ALAN': alan_chunk,
               'ADRI': adri_chunk,
               'LEVE': level9_chunk,
               'AGT ': agt_chunk,
               'MAGS': magnetic_scrolls_chunk,
               'ADVS': advsys_chunk,
               'EXEC': native_executable_chunk,
               'IFhd': game_identifier_chunk,
               'Plte': color_palette_chunk,
               'Fspc': frontispiece_chunk,
               'RDes': resource_description_chunk,
               'IFmd': metadata_chunk,
               'RelN': release_number_chunk,
               'Reso': resolution_chunk,
               'APal': adaptive_palette_chunk,
               'Loop': looping_chunk,
               'SNam': story_name_chunk,
               'GIF ': gif_chunk,
               'WAV ': wav_chunk,
               'MIDI': midi_chunk,
               'MP3 ': mp3_chunk
               }

form_types = {'IFRS': blorb_chunk,
              'AIFF': aiff_chunk
              }

game_ids = ['ZCOD', 'GLUL', 'TAD2', 'TAD3', 'HUGO', 'ALAN', 'ADRI', 'LEVE', 'AGT ', 'MAGS', 'ADVS', 'EXEC']

picture_ids = ['PNG ', 'JPEG', 'Rect', 'GIF ']

sound_ids = ['FORM', 'OGGV', 'MOD ', 'SONG', 'WAV ', 'MIDI', 'MP3 ']

data_ids = ['TEXT', 'BINA']

iff.chunk_types.update(chunk_types)
iff.form_types.update(form_types)


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


currentpalette = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                  (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]


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


class blorb:
    games = {}
    picts = {}
    sounds = {}

    def __init__(self, blorb_chunk):
        games = []
        picts = []
        sounds = []
        datas = []
        for c in blorb_chunk.sub_chunks:
            if c.ID == resource_index_chunk.ID:
                self.resource_index = c.resources[:]

            if c.ID in game_ids:
                games.append(c)
            if c.ID in picture_ids:
                picts.append(c)
            if c.ID in sound_ids:
                sounds.append(c)
            if c.ID in data_ids:
                datas.append(c)

            if c.ID == game_identifier_chunk.ID:
                pass
            if c.ID == color_palette_chunk.ID:
                pass
            if c.ID == frontispiece_chunk.ID:
                pass
            if c.ID == resource_description_chunk.ID:
                pass
            if c.ID == metadata_chunk.ID:
                pass
            if c.ID == release_number_chunk:
                pass
            if c.ID == resolution_chunk:
                pass
            if c.ID == adaptive_palette_chunk:
                pass
            if c.ID == looping_chunk:
                pass
            if c.ID == story_name_chunk:
                pass

        for a in range(rescount):
            usage = self.data[x + (a * 12):x + (a * 12) + 4]
            resnum = int.from_bytes(self.data[x + (a * 12) + 4:x + (a * 12) + 8], byteorder='big')
            pos = int.from_bytes(self.data[x + (a * 12) + 8:x + (a * 12) + 12], byteorder='big')
            try:
                self.resindex[usage][resnum] = pos
            except:
                self.resindex[usage] = {}
                self.resindex[usage][resnum] = pos

        x = self.findChunk(b'RelN')
        if x == 0:
            self.release = 0
        else:
            x += 8
            self.release = (self.data[x] << 8) + self.data[x + 1]

    def checkgame(self, game):
        x = self.findChunk(b'IFhd')
        if x == 0:
            return True
        x += 8
        idRelease = int.from_bytes(self.data[x:x + 2], byteorder='big')
        x += 2
        idSerial = self.data[x:x + 6]
        x += 6
        idChecksum = int.from_bytes(self.data[x:x + 2], byteorder='big')

        x = 2
        gameRelease = int.from_bytes(game[x:x + 2], byteorder='big')
        x = 0x12
        gameSerial = game[x:x + 6]
        x = 0x1C
        gameChecksum = int.from_bytes(game[x:x + 2], byteorder='big')
        if gameRelease == idRelease and gameSerial == idSerial and gameChecksum == idChecksum:
            return True
        return False

    def getExec(self, execnum):
        try:
            x = self.resindex[b'Exec'][execnum]
        except:
            return False
        size = self.chunkSize(x)
        data = self.data[x + 8:x + 8 + size]
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
        data = self.data[x + 8:x + 8 + size]
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
            data = self.data[x:x + 8 + size]
        else:
            data = self.data[x + 8:x + 8 + size]
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
            return 0  # effect
        return 1  # music

    def getWinSizes(self):
        x = self.findChunk(b'Reso')
        if x == 0:
            return None
        resosize = self.chunkSize(x)
        resochunk = self.data[x + 8:x + 8 + resosize]
        x = 0
        px = float(int.from_bytes(resochunk[x:x + 4], byteorder='big'))  # standard window width
        x += 4
        py = float(int.from_bytes(resochunk[x:x + 4], byteorder='big'))  # standard window height
        x += 4
        minx = int.from_bytes(resochunk[x:x + 4], byteorder='big')  # minimum window width
        x += 4
        miny = int.from_bytes(resochunk[x:x + 4], byteorder='big')  # minimum window height
        x += 4
        maxx = int.from_bytes(resochunk[x:x + 4], byteorder='big')  # maximum window width
        x += 4
        maxy = int.from_bytes(resochunk[x:x + 4], byteorder='big')  # maximum window height
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

        if (winx / px) < (winy / py):
            ERF = winx / px
        else:
            ERF = winy / py
        if (ERF * stdratio < minratio) and (minratio != 0):
            R = minratio
        elif (ERF * stdratio > maxratio) and (maxratio != 0):
            R = maxratio
        else:
            R = ERF * stdratio
        return R

    def getScaleData(self, picnum):
        x = self.findChunk(b'Reso')
        scaleData = {'ratnum': 1,
                     'ratden': 1,
                     'minnum': 1,
                     'minden': 1,
                     'maxnum': 1,
                     'maxden': 1
                     }
        if x == 0:
            return scaleData
        resosize = self.chunkSize(x)
        resochunk = self.data[x + 8:x + 8 + resosize]
        x = 24
        entrydata = resochunk[x:]

        entries = len(entrydata) // 28
        found = False

        for a in range(entries):
            b = a * 28
            entry = entrydata[b:b + 28]

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
        chunk = self.data[pos + 8:pos + 8 + csize]
        numentries = csize // 4
        entries = []
        for a in range(numentries):
            entries.append(int.from_bytes(chunk[4 * a:(4 * a) + 4], byteorder='big'))

        if picnum in entries:
            return currentpalette
        for a in range(2, len(palette)):
            if palette[a] != (0, 0, 0):
                currentpalette[a] = palette[a][:]
        return palette

    def findChunk(self, chunkname):
        id = None
        x = 12
        while (id != chunkname) and (x < len(self.data)):
            id = self.data[x:x + 4]
            csize = int.from_bytes(self.data[x + 4:x + 8], byteorder='big')
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
            id = self.data[x:x + 4]
            csize = int.from_bytes(self.data[x + 4:x + 8], byteorder='big')
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
        metadata = self.data[resoplace + 8:resoplace + 8 + resosize]
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
