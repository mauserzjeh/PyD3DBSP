import bpy
import bpy.ops
import bpy.props

from . import importer

class PyD3DBSP(bpy.types.Operator):
    bl_idname = 'pyd3dbsp.d3dbsp_importer'
    bl_label = 'CoD2 D3DBSP (.d3dbsp)'
    bl_options = {'UNDO'}


    filepath = bpy.props.StringProperty(subtype = 'FILE_PATH')
    filename_ext = '.d3dbsp'
    filter_glob = bpy.props.StringProperty(default="*.d3dbsp", options={'HIDDEN'})

    assetpath = bpy.props.StringProperty(
        name = 'Asset Path',
        description = 'Directory containing CoD2 assets.',
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