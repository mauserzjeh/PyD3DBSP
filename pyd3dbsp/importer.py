import math

import bpy
import bpy.ops
import bpy.props
import bmesh

from . import read_d3dbsp as D3DBSPREADER
from . import material as MATERIAL
from . import read_xmodel as XMODELREADER


def _create_mesh(surfaces, surface_name, prop=None, parent=None):
    if(prop):
        meshnull = bpy.data.objects.new(surface_name, None)
        bpy.context.scene.collection.objects.link(meshnull)

    for i in range(0, len(surfaces)):
        surface = surfaces[i]

        important_keys = set(['vertices', 'triangles'])
        if(important_keys.issubset(surface.keys())):
            mesh = bpy.data.meshes.new(surface_name)
            obj = bpy.data.objects.new(surface_name, mesh)
            
            bpy.context.scene.collection.objects.link(obj)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            mesh = bpy.context.object.data
            bm = bmesh.new()

            uv_surface_list = []
            vertexcolor_surface_list = []

            vertices = surface['vertices']
            triangles = surface['triangles']
            
            if('material' in surface):
                material = surface['material']
                obj.active_material = bpy.data.materials.get(material)
            
            for j in range(0, len(triangles)):
                triangle = triangles[j]

                vertex1 = vertices[triangle[0]]
                vertex2 = vertices[triangle[1]]
                vertex3 = vertices[triangle[2]]

                v1 = bm.verts.new(vertex1['position'])
                v2 = bm.verts.new(vertex2['position'])
                v3 = bm.verts.new(vertex3['position'])

                uv_triangle_list = []
                uv_triangle_list.append(vertex1['uv'])
                uv_triangle_list.append(vertex2['uv'])
                uv_triangle_list.append(vertex3['uv'])
                uv_surface_list.append(uv_triangle_list)

                vertexcolor_triangle_list = []
                vertexcolor_triangle_list.append(vertex1['color'])
                vertexcolor_triangle_list.append(vertex2['color'])
                vertexcolor_triangle_list.append(vertex3['color'])
                vertexcolor_surface_list.append(vertexcolor_triangle_list)

                bm.verts.ensure_lookup_table()
                bm.verts.index_update()

                bm.faces.new((v1, v2, v3))
                bm.faces.ensure_lookup_table()
                bm.faces.index_update()

            uv_layer = bm.loops.layers.uv.new()
            vertexcolor_layer = bm.loops.layers.color.new()

            for face, uv_face_data, vertexcolor_face_data in zip(bm.faces, uv_surface_list, vertexcolor_surface_list):
                for loop, uv_data, vertexcolor_data in zip(face.loops, uv_face_data, vertexcolor_face_data):
                    loop[uv_layer].uv = uv_data
                    loop[vertexcolor_layer] = vertexcolor_data

            bm.to_mesh(mesh)
            bm.free()

            if(prop):
                obj.parent = meshnull
                
                XMODELENUMS = XMODELREADER.XMODELENUMS
                
                if(XMODELENUMS.KEY_ORIGIN.value in prop):
                    obj.location = tuple(map(float, prop[XMODELENUMS.KEY_ORIGIN.value]))
                if(XMODELENUMS.KEY_ANGLES.value in prop):
                    rot_x = math.radians(float(prop[XMODELENUMS.KEY_ANGLES.value][0]))
                    rot_y = math.radians(float(prop[XMODELENUMS.KEY_ANGLES.value][1]))
                    rot_z = math.radians(float(prop[XMODELENUMS.KEY_ANGLES.value][2]))
                    obj.rotation_euler = (rot_x, rot_z, rot_y)
                if(XMODELENUMS.KEY_MODELSCALE.value in prop):
                    obj.scale = (float(prop[XMODELENUMS.KEY_MODELSCALE.value]), float(prop[XMODELENUMS.KEY_MODELSCALE.value]), float(prop[XMODELENUMS.KEY_MODELSCALE.value]))

            if(parent and prop):
                meshnull.parent = parent
            elif(parent and not prop):
                obj.parent = parent
        else:
            if(prop):
                bpy.data.objects.remove(meshnull, True)
            print("Surface " + surface_name + " #" + str(i) + " does not contain the necessary data.")

def _import_entities(entities, xmodelpath, xmodelsurfpath, materialpath, texturepath, parent=None, import_materials=True):
    XMODELENUMS = XMODELREADER.XMODELENUMS
    if(len(entities)):
        print('Importing entities...')
        nullname = parent.name + "_xmodels" if parent else "xmodels"
        entitiesnull = bpy.data.objects.new(nullname, None)
        bpy.context.scene.collection.objects.link(entitiesnull)

        if(parent):
            entitiesnull.parent = parent

        for i in range(0, len(entities)):
            entity = entities[i]
            if(XMODELENUMS.KEY_MODEL.value in entity):
                xmodel = XMODELREADER.XModel()
                if(xmodel.load_xmodel((xmodelpath + entity[XMODELENUMS.KEY_MODEL.value]), xmodelsurfpath)):
                    if(import_materials):
                        _import_materials(xmodel.materials, materialpath, texturepath)
                    _create_mesh(xmodel.surfaces, xmodel.modelname, prop=entity, parent=entitiesnull)

def _import_materials(materials, materialpath, texturepath):
    if(len(materials)):
        for material in materials:
            if(not (bpy.data.materials.get(material))):
                MATERIAL.create_material(material, materialpath, texturepath)

def import_d3dbsp(d3dbsppath, assetpath, import_materials=True, import_props=True):
    xmodelpath = assetpath + "xmodel\\"
    xmodelsurfpath = assetpath + "xmodelsurfs\\"
    texturepath = assetpath + "images\\"
    materialpath = assetpath + "materials\\"
    
    d3dbsp = D3DBSPREADER.D3DBSP()
    if(d3dbsp.load_d3dbsp(d3dbsppath)):

        d3dbspnull = bpy.data.objects.new(d3dbsp.mapname, None)
        bpy.context.scene.collection.objects.link(d3dbspnull)

        mapgeometrynull = bpy.data.objects.new(d3dbsp.mapname + "_geometry", None)
        bpy.context.scene.collection.objects.link(mapgeometrynull)

        mapgeometrynull.parent = d3dbspnull

        try:
            if(import_materials):
                print('Importing materials...')
                _import_materials(d3dbsp.materials, materialpath, texturepath)
            print('Creating map geometry...')
            _create_mesh(d3dbsp.surfaces, d3dbsp.mapname, parent=mapgeometrynull)
            if(import_props):
                _import_entities(d3dbsp.entities, xmodelpath, xmodelsurfpath, materialpath, texturepath, d3dbspnull, import_materials)
            return True
        except:
            return False