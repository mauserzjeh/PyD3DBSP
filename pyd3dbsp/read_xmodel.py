import struct
import os

from collections import namedtuple

XMODELSURFHeader = namedtuple('XMODELSURFHeader','version, mesh_number')
fmt_XMODELSURFHeader = '<HH'

XMODELSURFMeshHeader = namedtuple('XMODELSURFMeshHeader', 'num_verts, num_tris, num_verts2')
fmt_XMODELSURFMeshHeader = '<x3H'

class XModelSurface:
    def __init__(self):
        self.header = None
        self.meshes = []

    def _read_data(self, file):
        file.seek(0)
        header = file.read(struct.calcsize(fmt_XMODELSURFHeader))
        self.header = XMODELSURFHeader._make(struct.unpack(fmt_XMODELSURFHeader, header))
        if(self.header.version == 20):
            pass
        else:
            return False
        
    def load_xmodelsurface(self, filepath):
        with open(filepath, 'rb') as file:
            if(self._read_data(file)):
                return True
            else:
                return False

class XModel:
    def __init__(self):
        pass