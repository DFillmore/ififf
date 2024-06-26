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
        self.type = snd_chunk.ID.strip()
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

    resources = []

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        resource_count = int.from_bytes(self.raw_data[8:12], byteorder='big')
        self.resources = []
        for r in range(resource_count):
            usage = self.raw_data[12 + r * 12:16 + r * 12].decode('ascii')
            resource_number = int.from_bytes(self.raw_data[16 + r * 12:20 + r * 12], byteorder='big')
            location = int.from_bytes(self.raw_data[20 + r * 12:24 + r * 12], byteorder='big')
            self.resources.append(resource(usage, resource_number, location))


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
    palette: None | int | list = None

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        if self.length == 1:
            self.palette = int.from_bytes(self.raw_data[8], byteorder='big')
        else:
            self.palette = []
            colours = self.length // 3
            for c in range(colours):
                colour: dict[str, int] = {'red': int.from_bytes(self.raw_data[8 + c * 3], byteorder='big'),
                                          'green': int.from_bytes(self.raw_data[9 + c * 3], byteorder='big'),
                                          'blue': int.from_bytes(self.raw_data[10 + c * 3], byteorder='big')
                                         }
                self.palette.append(colour)

    def create_data(self):
        pass


class frontispiece_chunk(iff.chunk):
    ID = 'Fspc'
    picture_number = None

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
        p = 0
        while p < self.length:
            usage = int.from_bytes(self.raw_data[12 + p:16 + p], byteorder='big')
            try:
                self.entries[usage]
            except:
                self.entries[usage] = {}
            number = int.from_bytes(self.raw_data[16 + p:20 + p], byteorder='big')
            length = int.from_bytes(self.raw_data[20 + p:24 + p], byteorder='big')
            text = self.raw_data[24 + p:24 + p + length].decode('utf-8')
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

    screen = {}
    images: dict[int, dict] = {}

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.screen['standard_width'] = int.from_bytes(self.raw_data[8:12], byteorder='big')
        self.screen['standard_height'] = int.from_bytes(self.raw_data[12:16], byteorder='big')
        self.screen['minimum_width'] = int.from_bytes(self.raw_data[16:20], byteorder='big')
        self.screen['minimum_height'] = int.from_bytes(self.raw_data[20:24], byteorder='big')
        self.screen['maximum_width'] = int.from_bytes(self.raw_data[24:28], byteorder='big')
        self.screen['maximum_height'] = int.from_bytes(self.raw_data[28:32], byteorder='big')

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
    pictures = []

    def process_data(self):
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        palette_count = self.length // 4

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
    story_name = None

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
    images: dict[int, image] = {}
    sounds = {}

    screen: screen = screen()

    release = None
    serial = None
    checksum = None

    metadata = None

    currentpalette = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                      (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)
                     ]

    def __init__(self, blorb_chunk):
        c: iff.chunk
        for c in blorb_chunk.sub_chunks:
            if c.ID == resource_index_chunk.ID:
                c: resource_index_chunk

                res: resource
                for res in c.resources:
                    if res.usage == 'Exec':
                        self.games[res.number] = iff.chunk(iff.get_chunk(blorb_chunk, res.location))
                    if res.usage == 'Pict':
                        self.images[res.number] = image(iff.chunk(iff.get_chunk(blorb_chunk, res.location)), res.number)
                    if res.usage == 'Snd ':
                        sound_data = iff.get_chunk(blorb_chunk, res.location)[:]
                        if sound_data[:4] == b'FORM':
                            self.sounds[res.number] = sound(iff.chunk(sound_data), res.number)
                        else:
                            self.sounds[res.number] = sound(iff.chunk(sound_data[8:]), res.number)
            if c.ID == game_identifier_chunk.ID:
                c: game_identifier_chunk
                self.release = c.release_number
                self.serial = c.serial_number
                self.checksum = c.checksum

            if c.ID == color_palette_chunk.ID:
                c: color_palette_chunk
                self.color_palette = c.palette
            if c.ID == frontispiece_chunk.ID:
                c: frontispiece_chunk
                self.title_pic = c.picture_number
            if c.ID == resource_description_chunk.ID:
                pass
            if c.ID == metadata_chunk.ID:
                c: metadata_chunk
                self.metadata = c.xml[:]
            if c.ID == release_number_chunk.ID:
                c: release_number_chunk
                self.release = c.number
            if c.ID == resolution_chunk.ID:
                c: resolution_chunk

                self.screen.standard_width = c.screen['standard_width']
                self.screen.standard_height = c.screen['standard_height']
                self.screen.minimum_width = c.screen['minimum_width']
                self.screen.minimum_height = c.screen['minimum_height']
                self.screen.maximum_width = c.screen['maximum_width']
                self.screen.maximum_height = c.screen['maximum_height']

                for image_number in c.images:
                    try:
                        self.images[image_number].standard_numerator = c.images[image_number]['standard_numerator']
                        self.images[image_number].standard_denominator = c.images[image_number]['standard_denominator']
                        self.images[image_number].minimum_numerator = c.images[image_number]['minimum_numerator']
                        self.images[image_number].minimum_denominator = c.images[image_number]['minimum_denominator']
                        self.images[image_number].maximum_numerator = c.images[image_number]['maximum_numerator']
                        self.images[image_number].maximum_denominator = c.images[image_number]['maximum_denominator']
                    except:
                        pass

            if c.ID == adaptive_palette_chunk.ID:
                c: adaptive_palette_chunk
                self.adaptive_pictures = c.pictures

            if c.ID == looping_chunk.ID:
                c: looping_chunk
                for a in c.sound_looping_data:
                    self.sounds[a] = c.sound_looping_data[a]
            if c.ID == story_name_chunk.ID:
                c: story_name_chunk
                self.story_name = c.story_name

    def checkGame(self, game):
        if not self.release:  # if there's no IFhd chunk, any game will do
            return True

        gameRelease = int.from_bytes(game[2:4], byteorder='big')
        gameSerial = game[0x12:0x18]
        gameChecksum = int.from_bytes(game[0x1C:0x1E], byteorder='big')
        if gameRelease == self.release and gameSerial == self.serial and gameChecksum == self.checksum:
            return True
        return False

    def getExec(self, execnum):
        return self.games[execnum].data

    def getExecFormat(self, execnum):
        return self.games[execnum].type

    def getPict(self, picnum):
        return self.images[picnum].data

    def getPictFormat(self, picnum):
        return self.images[picnum].type

    def getSnd(self, sndnum):
        return self.sounds[sndnum].data

    def getSndFormat(self, sndnum):
        return self.sounds[sndnum].type

    def getSndType(self, sndnum):
        # AIFF Sounds = effect
        # Ogg Sounds = music
        # mod sounds = music
        # Song Sounds = music
        sformat = self.getSndFormat(sndnum)
        if sformat == 'FORM':  # aiff
            return 0  # effect
        return 1  # music

    def getWinSizes(self):
        return (self.screen.standard_width, self.screen.standard_height,
                self.screen.minimum_width, self.screen.minimum_height,
                self.screen.maximum_width, self.screen.maximum_height
               )

    def getScale(self, picnum, winx, winy):

        px, py, minx, miny, maxx, maxy = self.getWinSizes()

        ratnum = self.images[picnum].standard_numerator
        ratden = self.images[picnum].standard_denominator
        minnum = self.images[picnum].minimum_numerator
        minden = self.images[picnum].minimum_denominator
        maxnum = self.images[picnum].maximum_numerator
        maxden = self.images[picnum].maximum_denominator

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

    def adaptPalette(self, picnum, in_palette):
        in_palette = in_palette[:16]
        if not in_palette or not self.currentpalette:
            return in_palette

        if picnum in self.adaptive_pictures:
            return self.currentpalette

        for a in range(2, len(in_palette)):
            if in_palette[a] != (0, 0, 0):
                self.currentpalette[a] = in_palette[a][:]
        return in_palette

    def getMetaData(self):
        return self.metadata

    def getTitlePic(self):
        try:
            return self.images[self.title_pic]
        except:
            return None

