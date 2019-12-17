import bpy

from . import pyd3dbsp

bl_info = {
    "name": "CoD2D3DBSP Importer",
    "description": "Import Call of Duty 2 d3dbsp map files into blender.",
    "author": "Soma Rádóczi",
    "version": (0, 0, 1),
    "blender": (2, 81, 0),
    "location": "File > Import/Export",
    "category": "Import-Export",
    "warning": "This addon is still in development.",
    #"wiki_url": "",
}

classes = (
    pyd3dbsp.PyD3DBSP,
)

def menu_func_import_d3dbsp(self, context):
    self.layout.operator(pyd3dbsp.PyD3DBSP.bl_idname, text = "CoD2 D3DBSP map (.d3dbsp)")

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_d3dbsp)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_d3dbsp)

if __name__ == "__main__":
    unregister()
    register()