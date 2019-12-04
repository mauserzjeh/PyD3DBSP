import bpy
import bpy.ops
import bpy.props
import bmesh

from . import read_d3dbsp as D3DBSPREADER
from . import material as MATERIAL
from . import read_xmodel as XMODELREADER


def _create_mesh(surfaces, surface_name):

    for i in range(0, len(surfaces)):
        surface = surfaces[i]

        important_keys = set(['vertices', 'triangles'])
        if(important_keys.issubset(surface.keys())):
            mesh = bpy.data.meshes.new(surface_name)
            obj = bpy.data.objects.new(surface_name, mesh)

            bpy.context.scene.objects.link(obj)
            bpy.context.scene.objects.active = obj
            obj.select = True

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

            return obj
        else:
            print("Surface " + surface_name + " #" + str(i) + " does not contain the necessary data.")
 
def _import_entities(entities, xmodelpath, xmodelsurfpath, materialpath, texturepath):
    XMODELENUMS = XMODELREADER.XMODELENUMS
    if(len(entities)):
        for i in range(0, len(entities)):
            entity = entities[i]
            if(XMODELENUMS.KEY_MODEL.value in entity):
                xmodel = XMODELREADER.XModel()
                xmodel.load_xmodel((xmodelpath + entity[XMODELENUMS.KEY_MODEL.value]), xmodelsurfpath)

                _import_materials(xmodel.materials, materialpath, texturepath)
                xmodelobj = _create_mesh(xmodel.surfaces, xmodel.modelname)
                xmodelobj.location = entity[XMODELENUMS.KEY_ORIGIN.value]
                xmodelobj.rotation_euler = entity[XMODELENUMS.KEY_ANGLES.value]
                xmodelobj.scale = (entity[XMODELENUMS.KEY_MODELSCALE], entity[XMODELENUMS.KEY_MODELSCALE], entity[XMODELENUMS.KEY_MODELSCALE])

def _import_materials(materials, materialpath, texturepath):
    if(len(materials)):
        for material in materials:
            if(not (bpy.data.materials.get(material.name))):
                MATERIAL.create_material(material.name, materialpath, texturepath)

def import_d3dbsp(d3dbsppath, xmodelpath, xmodelsurfpath, materialpath, texturepath):
    d3dbsp = D3DBSPREADER.D3DBSP()
    d3dbsp.load_d3dbsp(d3dbsppath)
    
    #TODO ERROR HANDLING
    try:
        _import_materials(d3dbsp.materials, materialpath, texturepath)
        d3dbspobj = _create_mesh(d3dbsp.surfaces, d3dbsp.mapname)
        _import_entities(d3dbsp.entities, xmodelpath, xmodelsurfpath, materialpath, texturepath)
        return True
    except:
        return False
