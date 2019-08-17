# Copyright (C) 2001 - 2019 David Fillmore


def get_chunk(data, position):
    chunk_length = int.from_bytes(data[position+4:position+8], byteorder='big')
    c = data[position:position+8+chunk_length]
    return c

def split_chunks(data):
    """find all the top-level chunks in a bytes object, and return a list with each chunk as an item of bytes"""
    pos = 0
    chunks = []
    while pos < len(data):
        c = get_chunk(data, pos)
        pos += chunk_length + 8
        if len(c) % 2 == 1:
            pos += 1
        chunks.append(c)
    return chunks

class chunk:
    ID = "    "
    length = 0
    data = b''
    full_data = b'    \x00\x00\x00\x00'
    def from_bytes(self, raw_data):
        """given a bytes object containing an IFF chunk, return a chunk object of that data"""
        self.full_data = raw_data
        self.process_data()
        self.update_length()
        return self

    def to_bytes(self):
        """return a bytes object containing the chunk data"""
        # update data
        self.create_data()
        self.update_length()
        return self.full_data

    def process_data(self):
        """updates the various chunk attributes using the full_data"""
        self.ID = self.full_data[0:4].decode('ascii')
        self.length = int.from_bytes(self.full_data[4:8], byteorder='big')
        self.data = self.full_data[8:]

    def create_data(self):
        """updates the full_data using the chunk attributes"""
        self.full_data = self.ID.encode() + self.length.to_bytes(4, 'big') + self.data

    def update_length(self):
        self.length = len(self.full_data) - 8
        self.full_data = self.full_data[0:4] + self.length.to_bytes(4, 'big') + self.full_data[8:]
        
class form_chunk(chunk):
    ID = 'FORM'
    sub_chunks = []
    subID = '    '

    def process_data(self):
        """updates the various chunk attributes using the full_data"""
        #should check to see if ID is FORM and complain otherwise
        self.length = int.from_bytes(self.full_data[4:8], byteorder='big')
        self.subID = self.full_data[8:12].decode('ascii')
        self.data = self.full_data[12:]
        sub_chunks_data = split_chunks(self.data)
        self.sub_chunks = []
        # should use self.data to find all sub chunks, then process them
        for cd in sub_chunks_data:
            ID = cd[0:4].decode('ascii')
            if ID in chunk_types:
                co = chunk_types[ID]().from_bytes(cd)
            else:
                co = chunk().from_bytes(cd)
            self.sub_chunks.append(co)

    def create_data(self):
        chunks_data = []
        
        self.full_data = self.ID.encode() + self.length.to_bytes(4, 'big') + self.subID.decode()
        
        for co in self.sub_chunks():
            cd = co.to_bytes()
            self.full_data += cd
                
        
class text_chunk(chunk): # any chunk where the data is pure text
    def process_data(self):
        """updates the various chunk attributes using the full_data""" 
        self.length = int.from_bytes(self.full_data[4:8], byteorder='big')
        self.text = self.full_data[8:].decode('latin-1')

    def create_data(self):
        """updates the full_data using the chunk attributes"""
        self.full_data = self.ID.encode() + self.length.to_bytes(4, 'big') + self.text.encode()
    
class auth_chunk(text_chunk):
    ID = 'AUTH'


class anno_chunk(text_chunk):
    ID = 'ANNO'

class copy_chunk(text_chunk):
    ID = '(c) '

chunk_types = {'FORM':form_chunk,
               'AUTH':auth_chunk,
               'ANNO':anno_chunk,
               '(c) ':copy_chunk
              }
