# material creation code goes here

import bpy

import read_material
import read_texture

def create_material(name, material_fpath, texture_fpath):
    material_file = read_material.MTL()
    material_file.load_material(material_fpath + '\\' + name)
    
    material = bpy.data.materials.new(material_file.materialname)
    material.use_nodes = True

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # delete all nodes except output node
    for node in [node for node in nodes if node.type != 'OUTPUT_MATERIAL']:
        nodes.remove(node)

    # get output node
    material_output_node = None
    try:
        material_output_node = [node for node in nodes if node.type == 'OUTPUT_MATERIAL'][0]
    except:
        material_output_node = nodes.new('ShaderNodeOutputMaterial')
    material_output_node.location = (100,0)

    # create principled bsdf node
    principled_bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
    principled_bsdf_node.location = (-200,0)
    principled_bsdf_node.width = 200

    # create texture input nodes
    counter = 0
    for maptype, mapname in material_file.mapinfo.items():
        texture = read_texture.Texture()
        if(texture.load_texture(texture_fpath + '\\' + mapname + '.iwi')):
            texture_image = bpy.data.images.new(mapname, texture.width, texture.height)
            pixels = [x / 255 for x in texture.texture_data]
            texture_image.pixels = pixels

            texture_node = nodes.new('ShaderNodeTexImage')
            texture_node.label = maptype
            texture_node.location = (-700, 0 - 250 * counter)
            texture_node.image = texture_image

            counter += 1

    # create normalmap node
    normal_node = nodes.new('ShaderNodeNormalMap')
    normal_node.location = (-450, -500)

    # create texture coordinate node
    textcoord_node = nodes.new('ShaderNodeTexCoord')
    textcoord_node.location = (-1000, -150)

        

    """
    material = bpy.data.materials.new(material_file.materialname)
    material.use_nodes = True

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    for node in [node for node in nodes if node.type != 'OUTPUT_MATERIAL']:
        nodes.remove(node)
        
    material_output_node = None
    try:
        material_output_node = [node for node in nodes if node.type == 'OUTPUT_MATERIAL'][0]
    except:
        material_output_node = nodes.new('ShaderNodeOutputMaterial')
    material_output_node.location = (100, 0)

    principled_bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
    principled_bsdf_node.location = (-200,0)
    principled_bsdf_node.width = 200

    #colormap 
    colormap_node = nodes.new('ShaderNodeTexImage')
    colormap_node.location = (-700, 0)
    colormap_node.label = 'COLORMAP'

    #specularmap 
    specularmap_node = nodes.new('ShaderNodeTexImage')
    specularmap_node.location = (-700, -250)
    specularmap_node.label = 'SPECULARMAP'

    #normalmap 
    normalmap_node = nodes.new('ShaderNodeTexImage')
    normalmap_node.location = (-700, -500)
    normalmap_node.label = 'NORMALMAP'

    normal_node = nodes.new('ShaderNodeNormalMap')
    normal_node.location = (-450, -500)

    #textcoord
    textcoord_node = nodes.new('ShaderNodeTexCoord')
    textcoord_node.location = (-1000, -150)

    links.new(textcoord_node.outputs['UV'], colormap_node.inputs['Vector'])
    links.new(textcoord_node.outputs['UV'], specularmap_node.inputs['Vector'])
    links.new(textcoord_node.outputs['UV'], normalmap_node.inputs['Vector'])

    links.new(colormap_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
    links.new(specularmap_node.outputs['Color'], principled_bsdf_node.inputs['Specular'])
    links.new(normalmap_node.outputs['Color'], normal_node.inputs['Color'])
    links.new(normal_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])

    links.new(principled_bsdf_node.outputs['BSDF'], material_output_node.inputs['Surface'])
    """
# testing
create_material('toujane_ground1', 'F:\\MOVIEMAKING\\3D STUFF\\COD\\COD2ASSETS\\materials', 'F:\\MOVIEMAKING\\3D STUFF\\COD\\COD2ASSETS\\images')