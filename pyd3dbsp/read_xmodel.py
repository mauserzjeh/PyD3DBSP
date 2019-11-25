import struct
import os


from collections import namedtuple
from enum import Enum

from . import helper as HELPER

XMODELSURFHeader = namedtuple('XMODELSURFHeader','version, mesh_number')
fmt_XMODELSURFHeader = '<HH'

XMODELSURFMeshHeader = namedtuple('XMODELSURFMeshHeader', 'vertex_number, triangle_number, vertex_number2')
fmt_XMODELSURFMeshHeader = '<x3H'

class XMODELENUMS(Enum):
    VERSION = 20
    PHYSIQUED = 65535

class XModelSurface:
    def __init__(self):
        pass

    def _read_data(self, file):
        file.seek(0)
        header_data = file.read(struct.calcsize(fmt_XMODELSURFHeader))
        header = XMODELSURFHeader._make(struct.unpack(fmt_XMODELSURFHeader, header_data))

        if(header.version == XMODELENUMS.VERSION.value):
            meshes = []
            for i in range(header.mesh_number):
                current_mesh = {}

                mesh_header_data = file.read(struct.calcsize(fmt_XMODELSURFMeshHeader))
                mesh_header = XMODELSURFMeshHeader._make(struct.unpack(fmt_XMODELSURFMeshHeader, mesh_header_data))

                mesh_is_physiqued = False
                if(mesh_header.vertex_number2 == XMODELENUMS.PHYSIQUED.value):
                    mesh_is_physiqued = True
                
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

                current_mesh['triangles'] = []
                for l in range(mesh_header.triangle_number):
                    face = struct.unpack('<HHH', file.read(6))
                    current_mesh['triangles'].append(face)
                
                meshes.append(current_mesh)

            return meshes
        else:
            return False
        
    def load_xmodelsurface(self, filepath):
        try:
            with open(filepath, 'rb') as file:
                surfaces = self._read_data(file)
                return surfaces
        except:
            HELPER.file_not_found(filepath, "not found or some unhandled error occured.")

class XModel:
    def __init__(self):
        self.surfaces = []

    def _read_data(self, file):
        file.seek(0)
        version = struct.unpack('<H', file.read(2))[0]
        if(version == XMODELENUMS.VERSION.value):
            LODs = []
            file.read(25) #padding
            for i in range(4): #number of lods is always 4
                current_lod = {}
                current_lod['distance'] = struct.unpack('<f', file.read(4))[0]
                current_lod['name'] = HELPER.read_nullstr(file)

                if(len(current_lod['name'])):
                    LODs.append(current_lod)

            file.read(4) #padding
            pad_count = struct.unpack('<I', file.read(4))[0]
            for j in range(pad_count):
                subcount = struct.unpack('<I', file.read(4))[0]
                file.read(((subcount*48)+36)) #padding

            for k in range(len(LODs)):
                material_count = struct.unpack('<H', file.read(2))[0]
                current_lod_materials = []
                for l in range(material_count):
                    current_lod_materials.append(HELPER.read_nullstr(file))
                
                LODs[k]['materials'] = current_lod_materials
            
            return LODs
        else:
            return False

    def load_xmodel(self,filepath, xmodelsurfpath):
        try:
            with open(filepath, 'rb') as file:
                LODs = self._read_data(file)
                if(LODs):
                    xmodelsurface = XModelSurface()
                    LOD0 = LODs[0]
                    xmodelsurf = xmodelsurfpath + LOD0['name'] #using highest lod all the time
                    surfaces = xmodelsurface.load_xmodelsurface(xmodelsurf)

                    if(len(LOD0['materials']) == len(surfaces)):
                        for i in range(0, len(surfaces)):
                            surfaces[i]['material'] = LOD0['materials'][i]
                    else:
                        print("Mismatching number of LOD materials and surfaces. Materials will be omitted.")

                    self.surfaces = surfaces
                else:
                    return False
        except:
            HELPER.file_not_found(filepath, "not found or some unhandled error occured.")

    

