import gc
import math
import os
import struct

import bpy
import bpy.ops
import bpy.props
import bmesh

from . import importer

class PyD3DBSP(bpy.types.Operator):
    bl_idname = 'pyd3dbsp.d3dbsp_importer'
    bl_label = 'CoD2 D3DBSP (.d3dbsp)'
    bl_options = {'UNDO'}


    filepath = bpy.props.StringProperty(subtype = 'FILE_PATH')
    filename_ext = '.d3dbsp'
    filter_glob = bpy.props.StringProperty(default="*.d3dbsp", options={'HIDDEN'})

    materialPath = bpy.props.StringProperty(
        name = 'Material Path',
        description = 'Directory path containing the materials.',
        default = '',
        #subtype = 'DIR_PATH'
    )

    texturePath = bpy.props.StringProperty(
        name = 'Texture Path',
        description = 'Directory path containing the textures.',
        default = '',
        #subtype = 'DIR_PATH'
    )

    xmodelPath = bpy.props.StringProperty(
        name = 'Models Path',
        description = 'Directory path containing map entities.',
        default = '',
        #subtype = 'DIR_PATH'
    )

    def execute(self, context):
        #todo
        #result_import_d3dbsp = self.import_d3dbsp(context)
        #result_import_entities = import_entities()


        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}