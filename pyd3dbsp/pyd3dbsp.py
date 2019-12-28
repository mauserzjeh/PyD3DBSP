import bpy
import bpy.ops
import bpy.props

from . import importer as IMPORTER

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

    import_materials = bpy.props.BoolProperty(
        name = 'Import Materials',
        description = 'Whether to import materials and textures or not.',
        default = True
    )
    import_props = bpy.props.BoolProperty(
        name = 'Import Props',
        description = 'Whether to import props or not.',
        default = True
    )

    def execute(self, context):
        if(IMPORTER.import_d3dbsp(self.filepath, self.assetpath, self.import_materials, self.import_props)):
            print("Finished loading...")
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}