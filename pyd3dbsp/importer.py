import math

import bpy
import bpy.ops
import bpy.props
import bmesh

from . import read_d3dbsp as D3DBSPREADER
from . import material as MATERIAL
from . import read_xmodel as XMODELREADER
from . import helper as HELPER


def _create_mesh(surfaces, surface_name, prop=None, parent=None):
    """
    An all purpose mesh creating function suitable to process the read in data by D3DBSPREADER and XMODELREADER

    Parameters:
    -----------
    surfaces        - array/mixed   - Data containing all the necessary info of a mesh
    surface_name    - string        - Name of the surface
    prop            - array/mixed   - Parameter decides if we are importing a prop or not
    parent          - object/mixed  - Parameter for parenting
    -----------
    """

    # if we are importing a prop we create a null to parent all the meshes to
    if(prop):
        meshnull = bpy.data.objects.new(surface_name, None)
        bpy.context.scene.collection.objects.link(meshnull)

    # loop through surfaces
    for i in range(0, len(surfaces)):
        surface = surfaces[i]

        # main keys that are required to be present in the surface parameter
        important_keys = set(['vertices', 'triangles'])
        if(important_keys.issubset(surface.keys())):

            # create a mesh and link it to the scene/collection
            mesh = bpy.data.meshes.new(surface_name)
            obj = bpy.data.objects.new(surface_name, mesh)
            
            bpy.context.scene.collection.objects.link(obj)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            mesh = bpy.context.object.data
            bm = bmesh.new()

            # create lists for certain data
            uv_surface_list = []
            vertexcolor_surface_list = []

            # vertices
            vertices = surface['vertices']

            # triangles
            triangles = surface['triangles']
            
            # if we have a material set we set it as active material
            if('material' in surface):
                material = surface['material']
                obj.active_material = bpy.data.materials.get(material)
            
            # loop through the triangles
            for j in range(0, len(triangles)):
                triangle = triangles[j]

                # get vertices to form a triangle
                vertex1 = vertices[triangle[0]]
                vertex2 = vertices[triangle[1]]
                vertex3 = vertices[triangle[2]]

                # create vertices
                v1 = bm.verts.new(vertex1['position'])
                v2 = bm.verts.new(vertex2['position'])
                v3 = bm.verts.new(vertex3['position'])

                # create a list for the triangle UVs
                uv_triangle_list = []

                # get the UVs
                uv_triangle_list.append(vertex1['uv'])
                uv_triangle_list.append(vertex2['uv'])
                uv_triangle_list.append(vertex3['uv'])

                # add the UVs to the list
                uv_surface_list.append(uv_triangle_list)

                # create a list for the triangle vertex color
                vertexcolor_triangle_list = []

                # get the vertex color
                vertexcolor_triangle_list.append(vertex1['color'])
                vertexcolor_triangle_list.append(vertex2['color'])
                vertexcolor_triangle_list.append(vertex3['color'])

                # add the vertex color to the list
                vertexcolor_surface_list.append(vertexcolor_triangle_list)

                # update
                bm.verts.ensure_lookup_table()
                bm.verts.index_update()

                # create a new face (triangle)
                bm.faces.new((v1, v2, v3))

                # update
                bm.faces.ensure_lookup_table()
                bm.faces.index_update()

            # create UV layer
            uv_layer = bm.loops.layers.uv.new()

            # create vertex color layer
            vertexcolor_layer = bm.loops.layers.color.new()

            # loop through the faces and set the UV, vertex color data
            for face, uv_face_data, vertexcolor_face_data in zip(bm.faces, uv_surface_list, vertexcolor_surface_list):
                for loop, uv_data, vertexcolor_data in zip(face.loops, uv_face_data, vertexcolor_face_data):
                    loop[uv_layer].uv = uv_data
                    loop[vertexcolor_layer] = vertexcolor_data

            # finalize the mesh
            bm.to_mesh(mesh)
            bm.free()

            # if we have a prop we have a few things to setup
            if(prop):
                obj.parent = meshnull
                
                XMODELENUMS = XMODELREADER.XMODELENUMS
                
                # prop location
                if(XMODELENUMS.KEY_ORIGIN.value in prop):
                    obj.location = tuple(map(float, prop[XMODELENUMS.KEY_ORIGIN.value]))
                # prop rotation
                if(XMODELENUMS.KEY_ANGLES.value in prop):
                    rot_x = math.radians(float(prop[XMODELENUMS.KEY_ANGLES.value][0]))
                    rot_y = math.radians(float(prop[XMODELENUMS.KEY_ANGLES.value][1]))
                    rot_z = math.radians(float(prop[XMODELENUMS.KEY_ANGLES.value][2]))
                    obj.rotation_euler = (rot_x, rot_z, rot_y)
                # prop scale
                if(XMODELENUMS.KEY_MODELSCALE.value in prop):
                    obj.scale = (float(prop[XMODELENUMS.KEY_MODELSCALE.value]), float(prop[XMODELENUMS.KEY_MODELSCALE.value]), float(prop[XMODELENUMS.KEY_MODELSCALE.value]))
            # if we have a parent and we are importing a prop we set the meshnull's parent as parent
            if(parent and prop):
                meshnull.parent = parent
            # else if we have parent parameter but not importing a prop we set the created objects parent as parent
            elif(parent and not prop):
                obj.parent = parent
        else:
            # if we import a prop but it wesnt successful we remove the created null
            if(prop):
                bpy.data.objects.remove(meshnull, True)
            # give error message
            print("Surface " + surface_name + " #" + str(i) + " does not contain the necessary data.")

def _import_entities(entities, xmodelpath, xmodelsurfpath, materialpath, texturepath, parent=None, import_materials=True):
    """
    Function for importing props

    Parameters:
    -----------
    entities            - array/mixed   - Array containing data about props
    xmodelpath          - string        - Path to props
    xmodelsurfpath      - string        - Path to prop surfaces
    materialpath        - string        - Path to materials
    texturepath         - string        - Path to textures/images
    parent              - object/mixed  - Parent to parent to
    import_materials    - boolean       - Whether to import materials or not
    -----------
    """
    
    XMODELENUMS = XMODELREADER.XMODELENUMS
    # only start stuff if we have any props
    if(len(entities)):
        print('Importing entities...')
        # create null
        nullname = parent.name + "_xmodels" if parent else "xmodels"
        entitiesnull = bpy.data.objects.new(nullname, None)
        bpy.context.scene.collection.objects.link(entitiesnull)

        # parenting
        if(parent):
            entitiesnull.parent = parent

        # loop through the props
        for i in range(0, len(entities)):
            entity = entities[i]
            if(XMODELENUMS.KEY_MODEL.value in entity):
                # read/load prop data
                xmodel = XMODELREADER.XModel()
                # if loading was successful
                if(xmodel.load_xmodel((xmodelpath + entity[XMODELENUMS.KEY_MODEL.value]), xmodelsurfpath)):
                    # if we need to import materials
                    if(import_materials):
                        _import_materials(xmodel.materials, materialpath, texturepath)
                    # create prop mesh
                    _create_mesh(xmodel.surfaces, xmodel.modelname, prop=entity, parent=entitiesnull)

def _import_materials(materials, materialpath, texturepath):
    """
    Import materials

    Parameter:
    -----------
    materials       - list      - List of material names
    materialspath   - string    - Path to materials
    texturepath     - string    - Path to textures/images
    -----------
    """
    # only start if we have materials
    if(len(materials)):
        for material in materials:
            # only import material if it wasn't imported before
            if(not (bpy.data.materials.get(material))):
                MATERIAL.create_material(material, materialpath, texturepath)

def import_d3dbsp(d3dbsppath, assetpath, import_materials=True, import_props=True):
    """
    Main import function. Imports whole map and props depending on parameters.

    Parameters:
    -----------
    d3dbsppath          - string     - Path to the map file
    assetpath           - string     - Path to the assets folder structure
    import_materials    - boolean    - Whether to import materials or not
    import_props        - boolean    - Whether to import props or not
    -----------

    Returns:
    -----------
    Boolean - Whether importing was successful or not
    -----------
    """

    # define paths to certain required folders
    xmodelpath = assetpath + "xmodel\\"
    xmodelsurfpath = assetpath + "xmodelsurfs\\"
    texturepath = assetpath + "images\\"
    materialpath = assetpath + "materials\\"
    
    # create D3DBSP object
    d3dbsp = D3DBSPREADER.D3DBSP()

    # only start if loading was sucessful
    if(d3dbsp.load_d3dbsp(d3dbsppath)):
        
        # create a null that we will use as a parent
        d3dbspnull = bpy.data.objects.new(d3dbsp.mapname, None)
        bpy.context.scene.collection.objects.link(d3dbspnull)

        # create a null for the mapgeometry that we will parent the mapgeometry to
        mapgeometrynull = bpy.data.objects.new(d3dbsp.mapname + "_geometry", None)
        bpy.context.scene.collection.objects.link(mapgeometrynull)

        # set the parent
        mapgeometrynull.parent = d3dbspnull

        try:
            # if material import was true
            if(import_materials):
                # clean materials first
                HELPER.clean_materials()
                print('Importing materials...')
                # import materials
                _import_materials(d3dbsp.materials, materialpath, texturepath)
            print('Creating map geometry...')
            # create map geometry
            _create_mesh(d3dbsp.surfaces, d3dbsp.mapname, parent=mapgeometrynull)
            # if prop import was true
            if(import_props):
                # import props
                _import_entities(d3dbsp.entities, xmodelpath, xmodelsurfpath, materialpath, texturepath, d3dbspnull, import_materials)
            return True
        except:
            return False
    else:
        return False