import struct
import os


from collections import namedtuple
from enum import Enum

from . import helper as HELPER

"""
XMODELSURFHeader type definition. Used to store file header information.

Fields:
-------
version         - unsigned short - version (20) 
mesh_number     - unsigned short - number of meshes
-------
"""
XMODELSURFHeader = namedtuple('XMODELSURFHeader','version, mesh_number')
fmt_XMODELSURFHeader = '<HH'

"""
XMODELSURFMeshHeader type definition. Used to store mesh header information.

Fields:
-------
vertex_number   - unsigned short - number of vertices
triangle_number - unsigned short - number of triangles
vertex_number2  - unsigned short - another number of vertices (function currently not yet known)
-------
"""
XMODELSURFMeshHeader = namedtuple('XMODELSURFMeshHeader', 'vertex_number, triangle_number, vertex_number2')
fmt_XMODELSURFMeshHeader = '<x3H'

class XMODELENUMS(Enum):
    """
    XMODELENUMS class for storing some important values.
    """
    VERSION = 20 # version of the file
    PHYSIQUED = 65535 # physiqued value
    KEY_MODEL = 'model' # model key in entity string
    KEY_ANGLES = 'angles' # angles key in entity string
    KEY_ORIGIN = 'origin' # origin key in entity string
    KEY_MODELSCALE = 'modelscale' # modelscale key in entity string

class XModel:
    """
    XModel class for reading and storing data of Call of Duty 2 xmodel files.
    """
    def __init__(self):
        """
        Class constructor to initialize the class properties.

        Properties:
        -----------
        modelname   - string    - name of model
        surfaces    - list      - list of dictionaries containing surface info
        materials   - list      - list of material names
        -----------
        """
        self.modelname = ''
        self.surfaces = []
        self.materials = []

    def _read_surface_data(self, file):
        """
        Read surface data from file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------

        Returns:
        -----------
        False/List of surfaces wether the reading was successful or not
        -----------
        """
        file.seek(0)
        # read xmodelsurf header
        header_data = file.read(struct.calcsize(fmt_XMODELSURFHeader))
        header = XMODELSURFHeader._make(struct.unpack(fmt_XMODELSURFHeader, header_data))

        # validate version
        if(header.version == XMODELENUMS.VERSION.value):
            meshes = []
            # loop through the meshes
            for i in range(header.mesh_number):
                current_mesh = {}

                # read mesh header
                mesh_header_data = file.read(struct.calcsize(fmt_XMODELSURFMeshHeader))
                mesh_header = XMODELSURFMeshHeader._make(struct.unpack(fmt_XMODELSURFMeshHeader, mesh_header_data))

                # decide if the mesh is physiqued (props arent physiqued most of the time)
                mesh_is_physiqued = False
                if(mesh_header.vertex_number2 == XMODELENUMS.PHYSIQUED.value):
                    mesh_is_physiqued = True
                
                if(mesh_is_physiqued):
                    file.read(2) # padding
                
                # read in vertex data
                current_mesh['vertices'] = []
                for j in range(mesh_header.vertex_number):
                    vertex = {}
                    vertex['normal'] = struct.unpack('<fff', file.read(12))
                    vertex['color'] = struct.unpack('<BBBx', file.read(4))
                    vertex['uv'] = struct.unpack('<ff', file.read(8))
                    file.read(24) # padding

                    if(mesh_is_physiqued):
                        weight_count = struct.unpack('<B', file.read(1))[0]
                        file.read(2) # padding
                    
                    vertex['position'] = struct.unpack('<fff', file.read(12))

                    if(mesh_is_physiqued):
                        for k in range(weight_count):
                            file.read(16) # padding
                        if(weight_count):
                            file.read(1) # padding
                    
                    current_mesh['vertices'].append(vertex)

                # read in triangles
                current_mesh['triangles'] = []
                for l in range(mesh_header.triangle_number):
                    face = struct.unpack('<HHH', file.read(6))
                    current_mesh['triangles'].append(face)
                
                # store mesh
                meshes.append(current_mesh)

            # return meshes
            return meshes
        else:
            print(str(header.version) + " file version is not supported! (xmodelsurf)")
            return False
    
    def _load_xmodelsurface(self, filepath):
        """
        Load a Call of Duty 2 xmodelsurface for the xmodel

        Parameters:
        -----------
        filepath - string - Path to the file
        -----------
        """
        try:
            with open(filepath, 'rb') as file:
                # read xmodelsurf data
                surfaces = self._read_surface_data(file)
                # return the surface data
                return surfaces
        except:
            HELPER.file_not_found(filepath, " (xmodelsurf) not found or some unhandled error occured.")

    def _read_data(self, file):
        """
        Read xmodel data from file

        Parameters:
        -----------
        file - file object - file to read from
        -----------

        Returns:
        -----------
        False/List of LODs wether the reading was successful or not
        -----------
        """
        file.seek(0)
        # read version
        version = struct.unpack('<H', file.read(2))[0]
        if(version == XMODELENUMS.VERSION.value):
            LODs = []
            file.read(25) # padding
            # loop through LODs
            for i in range(4): # number of LODs is always 4
                
                # read in lod data
                current_lod = {}
                current_lod['distance'] = struct.unpack('<f', file.read(4))[0]
                current_lod['name'] = HELPER.read_nullstr(file)

                # only store valid LODs aka the ones that have name
                if(len(current_lod['name'])):
                    LODs.append(current_lod)

            file.read(4) # padding
            pad_count = struct.unpack('<I', file.read(4))[0]
            for j in range(pad_count):
                subcount = struct.unpack('<I', file.read(4))[0]
                file.read(((subcount*48)+36)) # padding

            # loop through valid LODs
            for k in range(len(LODs)):
                # read number of materials used by each lod
                material_count = struct.unpack('<H', file.read(2))[0]
                current_lod_materials = []
                # read in each LOD material names
                for l in range(material_count):
                    current_lod_materials.append(HELPER.read_nullstr(file))
                
                # store the materials to the LODs
                LODs[k]['materials'] = current_lod_materials
            
            # return LODs
            return LODs
        else:
            print(str(version) + " file version is not supported! (xmodel)")
            return False

    def load_xmodel(self, filepath, xmodelsurfpath):
        """
        Load a Call of Duty 2 xmodel

        Parameters:
        -----------
        filepath        - string - Path to the file
        xmodelsurfpath  - string - Path to the xmodelsurf file
        -----------

        Returns:
        --------
        Boolean - True/False wether the file reading was successful or not
        --------
        """
        try:
            with open(filepath, 'rb') as file:
                # get model name
                self.modelname = HELPER.return_filename_from_filepath(filepath, False)
                # read in LODs
                LODs = self._read_data(file)
                # if we have LODs
                if(LODs):
                    LOD0 = LODs[0] #using highest lod all the time
                    # get full path to the xmodelsurf that we have to read in
                    xmodelsurf = xmodelsurfpath + LOD0['name']
                    
                    # load the surfaces of the xmodelsurf
                    surfaces = self._load_xmodelsurface(xmodelsurf)

                    # we only care about materials if the ratio of surfaces and materials are 1:1
                    if(len(LOD0['materials']) == len(surfaces)):
                        for i in range(0, len(surfaces)):
                            surfaces[i]['material'] = LOD0['materials'][i]
                        # storing material names in a list for separate import 
                        self.materials = LOD0['materials']
                    else:
                        print("Mismatching number of LOD materials and surfaces. Materials will be omitted.")

                    # store surfaces
                    self.surfaces = surfaces
                    print(self.modelname + " is loaded.")
                    return True
                else:
                    return False
        except:
            HELPER.file_not_found(filepath, " (xmodel) not found or some unhandled error occured.")
            return False

