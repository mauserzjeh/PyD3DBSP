import bpy
import bpy.ops
import bpy.props
import bmesh

from . import read_d3dbsp
from . import create_material
from . import read_xmodel


def import_mesh(surfaces, surface_name):

    for i in range(0, len(surfaces)):
        mesh = bpy.data.meshes.new(surface_name)
        obj = bpy.data.objects.new(surface_name, mesh)

        bpy.context.scene.objects.link(obj)
        bpy.context.scene.objects.active = obj
        obj.select = True

        mesh = bpy.context.object.data
        bm = bmesh.new()

        uv_surface_list = []
        vertexcolor_surface_list = []

        surface = surfaces[i]

        important_keys = set(['vertices', 'triangles'])
        if(important_keys.issubset(surface.keys())):
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
        
        else:
            pass

        

def import_d3dbsp(self, context):
    pass
    
def import_entities(self, context):
    pass

def import_materials(self, materials, material_fpath, texture_fpath):
    if(len(materials)):
        if(len(bpy.data.materials)):
            for bpy_material in bpy.data.materials:
                bpy.data.materials.remove(bpy_material)
        
        for material in materials:
            if(not (bpy.data.materials.get(material.name))):
                create_material.create_material(material.name, material_fpath, texture_fpath)
