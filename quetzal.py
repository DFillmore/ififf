# Copyright (C) 2001 - 2019 David Fillmore

import copy
import os

from . import iff
from .ifchunks import ifhd_chunk
            
class z_memory:
    def __init__(self, current_data, original_data):
        self.full_data = bytes(current_data)
        self.original_data = bytes(original_data)

    def compress(self):
        changed_data = bytearray(a^b for a,b in zip(self.original_data, self.full_data))
        changed_data = changed_data.rstrip(b'\x00')

        compressed_data = bytearray()
        zerorun = 0
        for a in changed_data:
            if a == b'\x00':
                zerorun += 1
                if zerorun == 256:
                    zerorun -= 1
                    compressed_data.append('\x00')
                    compressed_data.append(zerorun.to_bytes(1, 'big'))
                    zerorun = 0
            else:
                if zerorun > 0:
                    zerorun -= 1
                    compressed_data.append(b'\x00')
                    compressed_data.append(zerorun.to_bytes(1, 'big'))
                    zerorun = 0
                compressed_data.append(a)

        self.compressed_data = bytes(compressed_data)

    def decompress(self):
        uncompressed_data = bytearray()
        zerorun = False
        for a in self.compressed_data:
            if zerorun:
                runlength = int.from_bytes(a, 'big')
                uncompressed_data.extend(bytes(runlength))
            else:
                if a == b'\x00':
                    zerorun = True
                uncompressed_data.append(a)
        uncompressed_data.extend(bytes(len(self.original_data) - len(uncompressed_data)))
        self.full_data = bytes(a^b for a,b in zip(uncompressed_data, self.original_data))
            
                    
            
class stkschunk(iff.chunk):
    ID = 'Stks'
    data = []
    def write(self):
        global zstack
        for a in range(len(storydata.callstack)):
            self.data.append((storydata.callstack[a].retPC >> 16) & 0xff)
            self.data.append((storydata.callstack[a].retPC >> 8) & 0xff)
            self.data.append(storydata.callstack[a].retPC & 0xff)
            self.data.append(storydata.callstack[a].flags)
            self.data.append(storydata.callstack[a].varnum)
            args = 1
            for b in range(storydata.callstack[a].numargs):
                args *= 2
            args -= 1
            self.data.append(args)
            self.data.append((storydata.callstack[a].evalstacksize >> 8) & 0xff)
            self.data.append(storydata.callstack[a].evalstacksize & 0xff)

            for x in range(len(storydata.callstack[a].lvars)):
                self.data.append((storydata.callstack[a].lvars[x] >> 8) & 255)
                self.data.append(storydata.callstack[a].lvars[x] & 255)
            
            for x in range(storydata.callstack[a].evalstacksize):
                self.data.append((storydata.callstack[a].evalstack[x] >> 8) & 255)
                self.data.append(storydata.callstack[a].evalstack[x] & 255)
        self.data.append((storydata.currentframe.retPC >> 16) & 0xff)
        self.data.append((storydata.currentframe.retPC >> 8) & 0xff)
        self.data.append(storydata.currentframe.retPC & 0xff)
        self.data.append(storydata.currentframe.flags)
        self.data.append(storydata.currentframe.varnum)
        args = 1
        for a in range(storydata.currentframe.numargs):
            args *= 2
        args -= 1
        self.data.append(args)
        self.data.append((len(storydata.currentframe.evalstack) >> 8) & 0xff)
        self.data.append(len(storydata.currentframe.evalstack) & 0xff)
        for x in range(len(storydata.currentframe.lvars)):
            self.data.append((storydata.currentframe.lvars[x] >> 8) & 255)
            self.data.append(storydata.currentframe.lvars[x] & 255)
            
        for x in range(storydata.currentframe.evalstacksize):
            self.data.append((storydata.currentframe.evalstack[x] >> 8) & 255)
            self.data.append(storydata.currentframe.evalstack[x] & 255)

    def read(self):
        global storydata
        # what we should do here is to read each frame back into a stack object
        # but, obviously, not *the* stack object, just in case something goes wrong.
        callstack = []
        place = 0
        while place < len(self.data):
            callstack.append(frame())
            callstack[-1].lvars = []
            callstack[-1].evalstack = []
            callstack[-1].retPC = (self.data[place] << 16) + (self.data[place+1] << 8) + self.data[place+2]
            callstack[-1].flags = self.data[place+3]
            numvars = self.data[place+3] & 15
            callstack[-1].varnum = self.data[place+4]
            done = 1
            x = 0
            args = self.data[place+5]
            while done != 0:
                x += 1
                done = args & 1
                args = args >> 1
            args -= 1
            callstack[-1].numargs = args
 
            callstack[-1].evalstacksize = (self.data[place+6] << 8) + self.data[place+7]
            
            place += 8
            for x in range(numvars): 
                
                callstack[-1].lvars.append((self.data[place] << 8) + self.data[place+1])
                place += 2
            
            for x in range(callstack[-1].evalstacksize):
                
                callstack[-1].evalstack.append((self.data[place] << 8) + self.data[place+1])
                place += 2
        storydata.callstack = copy.deepcopy(callstack)
        storydata.currentframe = storydata.callstack.pop()
        return callstack
        
        


class ifhdchunk(iff.chunk):
    ID = 'IFhd'
    length = 13
    rnumber = 0
    snumber = 0
    checksum = 0
    PC = 0
    data = []
    def write(self):
        
        self.data.append(storydata.release >> 8) # release number
        self.data.append(storydata.release & 255)

        for a in storydata.serial:
            self.data.append(ord(a))

        self.data.append(storydata.checksum >> 8)
        self.data.append(storydata.checksum & 255)

        self.data.append((storydata.PC >> 16) & 255)   # Initial PC
        self.data.append((storydata.PC >> 8) & 255)
        self.data.append(storydata.PC & 255)


    def read(self):
        global storydata
        if ((self.data[0] << 8) + self.data[1]) != storydata.release: # if the release number is wrong, fail
            return -1

        if self.data[2:8] != storydata.serial.encode('utf-8'): # if the serial number is wrong, fail
            return -1
        storydata.PC = (self.data[10] << 16) + (self.data[11] << 8) + self.data[12] 
        return storydata.PC

class intdchunk(iff.chunk):
    ID = 'IntD'
    osID = '    '
    flags = 0
    contID = 0
    reserved = 0
    terpID = '    '
    xdata = 0

class formchunk(iff.form_chunk):
    subID = 'IFZS'

    release = 0
    serial = '      '
    checksum = 0
    memory = []
    omemory = []
    callstack = []
    currentframe = None
    
    def write(self):
        self.data.append(ord('I')) 
        self.data.append(ord('F'))
        self.data.append(ord('Z'))
        self.data.append(ord('S'))
        chunks = [ ifhdchunk, umemchunk, stkschunk ] # chunks to write
        for a in range(len(chunks)):
            cchunk = chunks[a]() # set cchunk to current chunk
            cchunk.dowrite() # write current chunk's data
            id = cchunk.writeID() # set id to current chunk's ID
            for b in range(len(id)):
                self.data.append(ord(id[b])) # write current chunk's ID to data
            clen = cchunk.writelen() # write current

            
            for b in range(len(clen)):
                self.data.append(clen[b])
            for b in range(len(cchunk.data)):
                self.data.append(cchunk.data[b])

    def read(self):
        # okay, first, we need to check if this is an IFZS file
        if chr(self.data[0]) != 'I' or chr(self.data[1]) != 'F' or chr(self.data[2]) != 'Z' or chr(self.data[3]) != 'S':
            return -1
        
        data = self.data[4:]
        while len(data) > 0:
            cchunk = iff.chunk()
            cchunk.data = data
            clen = cchunk.readlen()
            id = cchunk.readID()
            
            if id == 'CMem':
                cchunk = cmemchunk()
                
            elif id == 'UMem':
                cchunk = umemchunk()
                
            elif id == 'Stks':
                cchunk = stkschunk()
                
            elif id == 'IFhd':
                cchunk = ifhdchunk()
            else:
                cchunk = iff.chunk()

            cchunk.data = data[8:clen+8]
            if clen % 2 == 1:
                data = data[clen+9:]
            else:
                data = data[clen+8:]
            
            if cchunk.read() == -1:
                return -1

###

class memory_chunk(iff.chunk):
    def process_data(self):
        """updates the various chunk attributes using the raw_data"""
        self.ID = self.raw_data[0:4].decode('ascii')
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.dynamic_memory = self.raw_data[8:self.length+8]

    def create_data(self):
        """updates the raw_data using the chunk attributes"""
        length = len(self.dynamic_memory)
        self.raw_data = self.ID.encode() + length.to_bytes(4, 'big') + self.dynamic_memory

    
class cmem_chunk(memory_chunk):
    ID = 'CMem'


class umem_chunk(memory_chunk):
    ID = 'UMem'

class frame:

    retPC = 0
    discard_result = False
    varnum = 0
    numargs = 0
    lvars = []
    evalstack = []

    def __init__(self, retPC, discard_result, varnum, numargs, lvars, evalstack):
        self.retPC = retPC
        self.discard_result = discard_result
        self.varnum = varnum
        self.numargs = numargs
        self.lvars = lvars[:]
        self.evalstack = evalstack[:]
        
class stks_chunk(iff.chunk):
    ID = 'Stks'
    callstack = []

    def process_data(self):
        self.ID = self.raw_data[0:4].decode('ascii')
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.callstack = []

        p = 8

        place = 0
        while place < len(self.raw_data):
            lvars = []
            evalstack = []
            
            retPC = int.from_bytes(self.raw_data[p:p+3], byteorder='big')

            numvars = self.raw_data[p+3] & 15
            if self.raw_data[p+3] & 16:
                discard_result = True
            else:
                discard_result = False

            varnum = self.raw_data[p+4]

            numargs = 0
            args = self.raw_data[p+5]
            while args > 0:
                numargs += 1
                args = args >> 1

            evalstacksize = int.from_bytes(self.raw_data[p+6:p+7], byteorder='big')
            
            p += 8
            for x in range(numvars): 
                lvars.append(int.from_bytes(self.raw_data[p:p+1], byteorder='big'))
                p += 2
            
            for x in range(evalstacksize):
                evalstack.append(int.from_bytes(self.raw_data[p:p+1], byteorder='big'))
                place += 2

            self.callstack.append(frame(retPC, discard_result, varnum, numargs, lvars, evalstack))

    def create_data(self):
        data = bytearray()
        data.extend(self.ID.encode())
        data.extend(self.length.to_bytes(4, 'big'))
        
        for f in self.callstack:
            data.extend(f.retPC.to_bytes(3, 'big'))
            flags = len(f.lvars)
            if f.discard_result:
                flags += 16
                    
            data.extend(flags.to_bytes(1, 'big'))
            
            data.extend(f.varnum.to_bytes(1, 'big'))
            
            args = 1
            for b in range(f.numargs):
                args *= 2
            args -= 1
            data.extend(args.to_bytes(1, 'big'))

            data.extend(len(f.evalstack).to_bytes(2, 'big'))

            for v in f.lvars:
                data.extend(v.to_bytes(2, 'big'))

            for e in f.evalstack:
                data.extend(e.to_bytes(2, 'big'))

        s = len(data) - 8
        data[4:8] = s.to_bytes(4, 'big')
        self.raw_data = bytes(data)
        

class intd_chunk(iff.chunk):
    ID = 'IntD'
    osID = '    '
    machine_specific = False
    do_not_copy = False
    contID = 0
    terpID = '    '
    data = 0

    def process_data(self):
        self.ID = self.raw_data[0:4].decode('ascii')
        self.length = int.from_bytes(self.raw_data[4:8], byteorder='big')
        self.OSid = self.raw_data[8:12].decode('ascii')
        flags = int.from_bytes(self.raw_data[12], byteorder='big')
        if flags & 1:
            self.do_not_copy = True
        else:
            self.do_not_copy = False
        if flags & 2:
            self.machine_specific = True
        else:
            self.machine_specific = False
        self.contID = int.from_bytes(self.raw_data[13], byteorder='big')
        self.OSid = self.raw_data[16:20].decode('ascii')
        self.data = self.raw_data[20:]

    def create_data(self):
        data = bytearray()
        data.extend(self.ID.encode())
        data.extend(self.length.to_bytes(4, 'big'))
        data.extend(self.osID.encode())
        flags = 0
        if self.do_not_copy:
            flags += 1
        if self.machine_specific:
            flags += 2
        data.extend(flags.to_bytes(1, 'big'))
        data.extend(self.contID.to_bytes(1, 'big'))
        data.extend(int(0).to_bytes(2, 'big'))
        data.extend(self.terpID.encode())
        data.extend(self.data)
        data[4:8] = len(data).to_bytes(4, 'big')
        self.raw_data = bytes(data)
        
        
                    
    

class quetzal_chunk(iff.form_chunk):
    subID = 'IFZS'

    ifhd = None
    cmem = None
    umem = None
    stks = None
    

    


class qdata:
    release = None
    serial = None
    checksum = None
    PC = None 
    current_memory = None
    orignial_memory = None
    callstack = None
    current_frame = None

def save(sfile, qd):
    global storydata
    # create a quetzal chunk
    # create chunks for each bit of data
    # add the sub-chunks to the quetzal chunk
    # process the quetzal chunk
    # write the quetzal chunk's data to file
    q = quetzal_chunk()

    # ifhd    
    g = ifhd_chunk()
    g.release_number = qd.release
    g.serial_number = qd.serial[:]
    g.checksum = qd.checksum
    g.PC = qd.PC
    q.ifhd = g

    
    
    # cmem
    m = cmem_chunk()
    q.memory = z_memory(qd.current_data, qd.original_data)
    q.compress()
    m.dynamic_memory = q.full_data[:]
    q.cmem = m
    
    # stks
    s = stks_chunk()
    

    return condition

def restore(savedata, qd):
    global storydata
    storydata = qd
    fchunk = formchunk()
    fchunk.data = savedata[8:]
    if fchunk.read() == -1:
        return False
    else:         
        return storydata

