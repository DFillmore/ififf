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

# contains IFF chunks common to multiple IF-related file types

from . import iff


class game_identifier_chunk(iff.chunk):  # common to blorb and quetzal files (only understands z-code IFhd chunks)
    ID = 'IFhd'
    length = 13
    release_number = 0
    serial_number = 0
    checksum = 0
    PC = 0

    def process_data(self):
        self.ID = self.raw_data[0:4].decode('ascii')
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.release_number = int.from_bytes(self.raw_data[8:10], byteorder='big')
        self.serial_number = self.raw_data[10:16].decode('ascii')
        self.checksum = int.from_bytes(self.raw_data[16:18], byteorder='big')
        self.PC = int.from_bytes(self.raw_data[18:21], byteorder='big')

    def create_data(self):
        data = bytearray()
        data.extend(self.ID.to_bytes(4, 'big'))
        data.extend(self.length.to_bytes(4, 'big'))
        data.extend(self.rnumber.to_bytes(2, 'big'))
        data.extend(self.snumber.encode())
        data.extend(self.checksum.to_bytes(2, 'big'))
        data.extend(self.length.PC(3, 'big'))

        self.raw_data = bytes(data)

