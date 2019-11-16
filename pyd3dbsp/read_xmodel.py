import struct
import os

from collections import namedtuple
from enum import Enum

XMODELSURFHeader = namedtuple('XMODELSURFHeader','version, mesh_number')
fmt_XMODELSURFHeader = '<HH'

XMODELSURFMeshHeader = namedtuple('XMODELSURFMeshHeader', 'vertex_number, triangle_number, vertex_number2')
fmt_XMODELSURFMeshHeader = '<x3H'

class XMODELENUMS(Enum):
    VERSION = 20
    PHYSIQUED = 65535

class XModelSurface:
    def __init__(self):
        self.header = None
        self.meshes = []

    def _read_data(self, file):
        file.seek(0)
        header_data = file.read(struct.calcsize(fmt_XMODELSURFHeader))
        self.header = XMODELSURFHeader._make(struct.unpack(fmt_XMODELSURFHeader, header_data))

        if(self.header.version == XMODELENUMS.VERSION.value):
            for i in range(self.header.mesh_number):
                current_mesh = {}

                mesh_header_data = file.read(struct.calcsize(fmt_XMODELSURFMeshHeader))
                mesh_header = XMODELSURFMeshHeader._make(struct.unpack(fmt_XMODELSURFMeshHeader, mesh_header_data))

                current_mesh['header'] = mesh_header

                mesh_is_physiqued = False
                if(mesh_header.vertex_number2 == XMODELENUMS.PHYSIQUED.value):
                    mesh_is_physiqued = True
                
                current_mesh['physiqued'] = mesh_is_physiqued

                if(mesh_is_physiqued):
                    file.read(2) #padding
                
                current_mesh['vertices'] = []
                for j in range(mesh_header.vertex_number):
                    vertex = {}
                    vertex['normal'] = struct.unpack('<fff', file.read(12))
                    vertex['color'] = struct.unpack('<BBBB', file.read(4))
                    vertex['uv'] = struct.unpack('<ff', file.read(8))
                    file.read(24) #padding

                    if(mesh_is_physiqued):
                        weight_count = struct.unpack('<B', file.read(1))[0]
                        file.read(2) #padding
                    
                    vertex['position'] = struct.unpack('<fff', file.read(12))

                    if(mesh_is_physiqued):
                        for k in range(weight_count):
                            file.read(16) #TODO reverse weights - padding
                        if(weight_count):
                            file.read(1) #padding
                    
                    #vertex['weights'] = [] #TODO reverse weights - placeholder
                    current_mesh['vertices'].append(vertex)

                current_mesh['faces'] = []
                for l in range(mesh_header.triangle_number):
                    face = struct.unpack('<HHH', file.read(6))
                    current_mesh['faces'].append(face)
                
                self.meshes.append(current_mesh)
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
        self.header = None
    
