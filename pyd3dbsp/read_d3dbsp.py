import struct
import os
import re

from collections import namedtuple
from enum import Enum

from . import helper as HELPER

"""
D3DBSPHeader type definition. Used to store file header information.

Fields:
-------
magic   - 4 byte string - file magic (IBSP) 
version - integer       - file version (4)  
-------

"""
D3DBSPHeader = namedtuple('D3DBSPHeader', 'magic, version')
fmt_D3DBSPHeader = '<4si' # D3DBSPHeader format

"""
D3DBSPLump type definition. Used to store lump information.

Fields:
-------
length - unsigned integer - lump length
offset - unsigned integer - lump offset (from the beginning of the file)
-------

"""
D3DBSPLump = namedtuple('D3DBSPLump', 'length, offset')
fmt_D3DBSPLump = '<2I' # D3DBSPLump format

"""
D3DBSPMaterial type definition. Used to store material information.

Fields:
-------
name    - 64 byte string        - material name
flags   - unsigned long long    - material flags
-------

"""
D3DBSPMaterial = namedtuple('D3DBSPMaterial', 'name, flags')
fmt_D3DBSPMaterial = '<64sQ' # D3DBSPMaterial format

"""
D3DBSPTriangle type definition. Used to store triangle information.

Fields:
-------
v1 - unsigned short - first index
v2 - unsigned short - second index
v3 - unsigned short - third index
-------

"""
D3DBSPTriangle = namedtuple('D3DBSPTriangle', 'v1, v2, v3')
fmt_D3DBSPTriangle = '<3H' # D3DBSPTriangle format

"""
D3DBSPTriangleSoup type definition. Used to store trianglesoup information.

Fields:
-------
material_id     - unsigned short    - material id
draw_order      - unsigned short    - draw order
vertex_offset   - unsigned integer  - vertex offset
vertex_length   - unsigned short    - vertex length
triangle_length - unsigned short    - triangle length
triangle_offset - unsigned integer  - triangle offset
-------

"""
D3DBSPTriangleSoup = namedtuple('D3DBSPTriangleSoup', 
    ('material_id, draw_order,'
    'vertex_offset, vertex_length,'
    'triangle_length, triangle_offset')
    )
fmt_D3DBSPTriangleSoup = '<HHIHHI' # D3DBSPTriangleSoup format


"""
D3DBSPVertex type definition. Used to store vertex information.

Fields:
-------
pos_x       - float         - Position X
pos_y       - float         - Position Y
pos_z       - float         - Position Z
norm_x      - float         - Normal X
norm_y      - float         - Normal Y
norm_z      - float         - Normal Z
clr_r       - unsigned char - Color red
clr_g       - unsigned char - Color green
clr_b       - unsigned char - Color blue
clr_a       - unsigned char - Color alpha
uv_u        - float         - UV U
uv_v        - float         - UV V
st_s        - float         - ST S
st_t        - float         - ST T
unknwn_1    - float         - Unknown 1
unknwn_2    - float         - Unknown 2
unknwn_3    - float         - Unknown 3
unknwn_4    - float         - Unknown 4
unknwn_5    - float         - Unknown 5
unknwn_6    - float         - Unknown 6
-------

"""
D3DBSPVertex = namedtuple('D3DBSPVertex',
    ('pos_x, pos_y, pos_z,'
    'norm_x, norm_y, norm_z,'
    'clr_r, clr_g, clr_b, clr_a,'
    'uv_u, uv_v,'
    'st_s, st_t,'
    'unknwn_1, unknwn_2, unknwn_3, unknwn_4, unknwn_5, unknwn_6')
    )
fmt_D3DBSPVertex = '<3f3f4B2f2f6f' # D3DBSPVertex format

class LUMP(Enum):
    """
    LUMP Enum class to store the lumps and their indexes represented in the D3DBSP file.
    """
    
    MATERIALS = 0
    LIGHTMAPS = 1
    LIGHT_GRID_HASH = 2
    LIGHT_GRID_VALUES = 3
    PLANES = 4
    BRUSHSIDES = 5
    BRUSHES = 6
    TRIANGLESOUPS = 7
    VERTICES = 8
    TRIANGLES = 9
    CULL_GROUPS = 10
    CULL_GROUP_INDEXES = 11
    PORTAL_VERTS = 17
    OCCLUDER = 18
    OCCLUDER_PLANES = 19
    OCCLUDER_EDGES = 20
    OCCLUDER_INDEXES = 21
    AABB_TREES = 22
    CELLS = 23
    PORTALS = 24
    NODES = 25
    LEAFS = 26
    LEAF_BRUSHES = 27
    COLLISION_VERTS = 29
    COLLISION_EDGES = 30
    COLLISION_TRIS = 31
    COLLISION_BORDERS = 32
    COLLISION_PARTS = 33
    COLLISION_AABBS = 34
    MODELS = 35
    VISIBILITY = 36
    ENTITIES = 37
    PATHS = 38

class D3DBSPENUMS(Enum):
    """
    D3DBSPENUMS class for storing some important values.
    """
    MAGIC = 'IBSP'
    VERSION = 4

class D3DBSP:
    """
    D3DBSP class for reading and storing data of Call of Duty 2 .d3dbsp files.
    """

    def __init__(self):
        """
        Class constructor to initialize the class properties.

        Properties:
        -----------
        mapname         - string        - name of the map
        surfaces        - list          - list of dictionaries containing surface info
        entities        - list          - list of dictionaries containing entity info
        materials       - list          - list of materials names
        -----------
        """
        self.mapname = ''
        self.surfaces = []
        self.entities = []
        self.materials = []

    def _read_header(self, file):
        """
        Read header data from file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------

        Returns:
        --------
        Namedtuple - Header magic and version
        --------
        """
        file.seek(0)
        header_data = file.read(struct.calcsize(fmt_D3DBSPHeader))
        header = D3DBSPHeader._make(struct.unpack(fmt_D3DBSPHeader, header_data))
        # decode header magic to string
        header = header._replace(magic = header.magic.decode('utf-8'))
        return header
    
    def _read_lumps(self, file):
        """
        Read lump list from file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------

        Returns:
        --------
        List - list of lumps
        --------
        """
        file.seek(struct.calcsize(fmt_D3DBSPHeader), os.SEEK_SET)
        lumps = []
        for i in range(39): # there are 39 lumps in the CoD2 .d3dbsp file
            lump_data = file.read(struct.calcsize(fmt_D3DBSPLump))
            lump = D3DBSPLump._make(struct.unpack(fmt_D3DBSPLump, lump_data))
            lumps.append(lump)
        return lumps

    def _read_materials(self, file, lumps):
        """
        Read materials from file.

        Parameters:
        -----------
        file    - file object   - File to read from
        lumps   - list          - List of lumps
        -----------

        Returns:
        --------
        List - list of materials
        --------
        """

        material_lump = lumps[LUMP.MATERIALS.value]
        materials = []
        file.seek(material_lump.offset, os.SEEK_SET)
        for i in range(0, material_lump.length, struct.calcsize(fmt_D3DBSPMaterial)):
            material_data = file.read(struct.calcsize(fmt_D3DBSPMaterial))
            material = D3DBSPMaterial._make(struct.unpack(fmt_D3DBSPMaterial, material_data))
            # decode material names and remove pad bytes
            material = material._replace(name = material.name.decode('utf-8').rstrip('\x00'))
            materials.append(material)
        return materials

    def _read_trianglesoups(self, file, lumps):
        """
        Read trianglesoups from file.

        Parameters:
        -----------
        file    - file object   - File to read from
        lumps   - list          - List of lumps
        -----------

        Returns:
        --------
        List - list of trianglesoups
        --------
        """

        trianglesoups_lump = lumps[LUMP.TRIANGLESOUPS.value]
        trianglesoups = []
        file.seek(trianglesoups_lump.offset, os.SEEK_SET)
        for i in range(0, trianglesoups_lump.length, struct.calcsize(fmt_D3DBSPTriangleSoup)):
            trianglesoup_data = file.read(struct.calcsize(fmt_D3DBSPTriangleSoup))
            trianglesoup = D3DBSPTriangleSoup._make(struct.unpack(fmt_D3DBSPTriangleSoup, trianglesoup_data))
            trianglesoups.append(trianglesoup)
        return trianglesoups

    def _read_vertices(self, file, lumps):
        """
        Read vertices from file.

        Parameters:
        -----------
        file    - file object   - File to read from
        lumps   - list          - List of lumps
        -----------

        Returns:
        --------
        List - list of vertices
        --------
        """

        vertices_lump = lumps[LUMP.VERTICES.value]
        vertices = []
        file.seek(vertices_lump.offset, os.SEEK_SET)
        for i in range(0, vertices_lump.length, struct.calcsize(fmt_D3DBSPVertex)):
            vertex_data = file.read(struct.calcsize(fmt_D3DBSPVertex))
            vertex = D3DBSPVertex._make(struct.unpack(fmt_D3DBSPVertex, vertex_data))
            vertices.append(vertex)
        return vertices

    def _read_triangles(self, file, lumps):
        """
        Read triangles from file.

        Parameters:
        -----------
        file    - file object   - File to read from
        lumps   - list          - List of lumps
        -----------
        
        Returns:
        --------
        List - list of triangles
        --------
        """

        triangles_lump = lumps[LUMP.TRIANGLES.value]
        triangles = []
        file.seek(triangles_lump.offset, os.SEEK_SET)
        for i in range(0, triangles_lump.length, struct.calcsize(fmt_D3DBSPTriangle)):
            triangle_data = file.read(struct.calcsize(fmt_D3DBSPTriangle))
            triangle = D3DBSPTriangle._make(struct.unpack(fmt_D3DBSPTriangle, triangle_data))
            triangles.append(triangle)
        return triangles

    def _read_entities(self, file, lumps):
        """
        Read entities from file.

        Parameters:
        -----------
        file    - file object   - File to read from
        lumps   - list          - List of lumps
        -----------
        
        Returns:
        --------
        List - list of entities
        --------
        """

        entities_lump = lumps[LUMP.ENTITIES.value]
        entities = []
        file.seek(entities_lump.offset, os.SEEK_SET)
        entity_data = file.read(entities_lump.length)
        # decode the whole entity data into a single string and remove pad bytes
        entity_str = entity_data.decode('utf-8').rstrip('\x00')
        for i in range(0, len(entity_str)):
            entity_substr = ''
            # split up entity string into single entity substrings
            if(entity_str[i] == '{' and entity_str[i+1] == '\n'):
                i += 2
                while(entity_str[i] != '}'):
                    entity_substr += entity_str[i]
                    i += 1
                # make a dictionary out of key value pairs
                entity = dict(re.findall('\"(.*?)\"\s\"(.*?)\"\n', entity_substr))
                # if the value of the key contains x, y, z coordinate values
                # then make a list out of it, so its easier to access those values
                for k, v in entity.items():
                    if(re.match('([-.0-9e]+\s[-.0-9e]+\s[-.0-9e]+)', v)):
                        entity[k] = v.split(' ')
                    # remove xmodel/ from the modelname
                    modelname = re.match('^xmodel\/(.*)', v)
                    if(modelname):
                        entity[k] = modelname.group(1)
                entities.append(entity)
        return entities
    
    def _create_surfaces(self, materials, trianglesoups, vertices, triangles):
        """
        Create surface data from the read data.

        Parameters:
        -----------
        materials       - list - list of materials
        trianglesoups   - list - list of trianglesoups
        vertices        - list - list of vertices
        triangles       - list - list of triangles
        -----------

        Returns:
        --------
        List - list of surfaces
        --------
        """
        surfaces = [] # a trianglesoup describes a surface
        # loop through the trianglesoups
        for i in range(0, len(trianglesoups)):
            surface = {}

            # select current trianglesoup (surface)
            trianglesoup = trianglesoups[i]

            # get the material used by the surface
            surface['material'] = materials[trianglesoup.material_id].name
            # create list for triangles in the surface
            surface['triangles'] = []
            # create dictionary for vertices in the surface
            surface['vertices'] = {}
            # triangle count of the surface
            triangle_count = (int) (trianglesoup.triangle_length / 3)

            # loop through the triangles
            for j in range(0, triangle_count):
                
                # get the current triangle id
                triangle_id = (int) (trianglesoup.triangle_offset / 3 + j)
                # get the current triangle
                triangle = triangles[triangle_id]
                
                # get 3 vertex id to create a triangle
                vertex1_id = (int) (trianglesoup.vertex_offset + triangle.v1)
                vertex2_id = (int) (trianglesoup.vertex_offset + triangle.v2)
                vertex3_id = (int) (trianglesoup.vertex_offset + triangle.v3)
                
                # store the vertex ids for the triangle
                surface['triangles'].append((vertex1_id, vertex2_id, vertex3_id))

                # loop through each vertex id
                for k in (vertex1_id, vertex2_id, vertex3_id):
                    vertex = {}
                    
                    # get the vertex
                    vert = vertices[k]

                    # store the vertex data
                    vertex['normal'] = (vert.norm_x, vert.norm_y, vert.norm_z)
                    vertex['color'] = (vert.clr_r / 255, vert.clr_g / 255, vert.clr_b / 255, vert.clr_a / 255)
                    vertex['uv'] = (vert.uv_u, vert.uv_v)
                    vertex['position'] = (vert.pos_x, vert.pos_y, vert.pos_z)

                    # store the vertex
                    surface['vertices'][k] = vertex

            # store the surface
            surfaces.append(surface)
        # return the surfaces
        return surfaces

    def load_d3dbsp(self, filepath):
        """
        Load a Call of Duty 2 .d3dbsp file and read all the necessary data from it.

        Parameters:
        -----------
        filepath - string - Path to the file
        -----------

        Returns:
        --------
        Boolean - True/False wether the file reading was successful or not
        --------
        """
        try:
            with open(filepath, 'rb') as file:
                # get map name
                self.mapname = HELPER.return_filename_from_filepath(filepath, False)
                header = self._read_header(file)
                # validate CoD2 .d3dbsp format
                if(header.magic == D3DBSPENUMS.MAGIC.value and header.version == D3DBSPENUMS.VERSION.value):
                    # read lumps
                    lumps = self._read_lumps(file)
                    # read materials and store the names in a list for a separate import
                    materials = self._read_materials(file, lumps)
                    for i in range(0, len(materials)):
                        self.materials.append(materials[i].name)

                    # read trianglesoups
                    trianglesoups = self._read_trianglesoups(file, lumps)
                    # read vertices
                    vertices = self._read_vertices(file, lumps)
                    # read triangles
                    triangles = self._read_triangles(file, lumps)
                    # read entities
                    self.entities = self._read_entities(file, lumps)
                    # create surfaces
                    self.surfaces = self._create_surfaces(materials, trianglesoups, vertices, triangles)
                    print(self.mapname + " is loaded.")
                    return True
                else:
                    print(header.magic + str(header.version) + " file version is not supported! (d3dbsp)")
                    return False
        except:
            HELPER.file_not_found(filepath, "not found or some unhandled error occured.")
            return False