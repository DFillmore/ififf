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

def get_chunk(data, position=0):
    chunk_length = int.from_bytes(data[position + 4:position + 8], byteorder='big')
    if chunk_length % 2 == 1:
        chunk_length += 1
    c = data[position:position + 8 + chunk_length]
    return c


def split_chunks(data):
    """find all the top-level chunks in a bytes object, and return a list with each chunk as an item of bytes"""
    pos = 0
    chunks = []
    while pos < len(data):
        c = get_chunk(data, pos)
        pos += len(c)
        chunks.append(c)
    return chunks


def identify_chunk(c):
    if c.ID in chunk_types:
        return chunk_types[c.ID](c.raw_data)
    return c


class chunk:
    ID = "    "
    length = 0
    data = b''
    raw_data = b'    \x00\x00\x00\x00'

    def __repr__(self):
        return self.ID + ' chunk'

    def __init__(self, chunk_data=None):
        if chunk_data:
            self.raw_data = get_chunk(chunk_data)
        self.process_data()

    def get_chunk_data(self):
        """return a bytes object containing the chunk data"""
        self.create_data()
        self.pad_data()
        return self.raw_data

    def pad_data(self):
        if len(self.raw_data) % 2 == 1:
            self.raw_data += b'\x00'

    def process_data(self):
        """updates the various chunk attributes using the raw_data"""
        self.ID = self.raw_data[0:4].decode('ascii')
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.data = self.raw_data[8:self.length + 8]

    def create_data(self):
        """updates the raw_data using the chunk attributes"""
        length = len(self.data) + 8
        self.raw_data = self.ID.encode() + length.to_bytes(4, 'big') + self.data


class form_chunk(chunk):
    ID = 'FORM'
    sub_chunks = []
    subID = '    '

    def __str__(self):
        return self.ID + ' ' + self.subID + ' chunk'

    def process_data(self):
        """updates the various chunk attributes using the raw_data"""
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        subID = self.raw_data[8:12].decode('ascii')
        self.subID = subID
        self.data = self.raw_data[12:self.length + 12]
        sub_chunks_data = split_chunks(self.data)
        self.sub_chunks: list[chunk] = []

        for cd in sub_chunks_data:
            co = chunk(cd)
            co = identify_chunk(co)
            self.sub_chunks.append(co)

    def create_data(self):
        temp_data = bytes(self.subID, 'ascii')

        for co in self.sub_chunks:
            cd = co.get_chunk_data()
            temp_data += cd
        length = len(temp_data)
        self.raw_data = self.ID.encode() + length.to_bytes(4, 'big') + temp_data

    def find_chunk(self, ID, ordinal=1):
        for a in self.sub_chunks:
            if a.ID == ID:
                if ordinal <= 1:
                    return a
                ordinal -= 1
        return None


class text_chunk(chunk):  # any chunk where the data is pure text
    encoding = 'latin-1'
    text = ''

    def process_data(self):
        """updates the various chunk attributes using the raw_data"""
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.text = self.raw_data[8:self.length + 8].decode(self.encoding)

    def create_data(self):
        """updates the raw_data using the chunk attributes"""
        length = len(self.text.encode()) + 8
        self.raw_data = self.ID.encode() + self.length.to_bytes(length, 'big') + self.text.encode()


class auth_chunk(text_chunk):
    ID = 'AUTH'


class anno_chunk(text_chunk):
    ID = 'ANNO'


class copy_chunk(text_chunk):
    ID = '(c) '


chunk_types = {'FORM': form_chunk,
               'AUTH': auth_chunk,
               'ANNO': anno_chunk,
               '(c) ': copy_chunk
               }

form_types = {}
