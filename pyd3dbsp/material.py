# material creation code goes here

import bpy

from . import read_material as MATERIALREADER
from . import read_texture as TEXTUREREADER

def create_material(name, material_fpath, texture_fpath):
    """
    All purpose material creation function. Reads in the necessary textures and creates a suitable shadernode setup.


    Parameters:
    -----------
    name            - string - Name of the material
    material_fpath  - string - Path to the material file to read from
    texture_fpath   - string - Path to the the textures to read
    -----------
    """

    # variable for error handling
    material_loading = True

    # create material object
    material_file = MATERIALREADER.MTL()

    # try to load the material
    try:
        material_file.load_material(material_fpath + name)
    except:
        print("Couldn't load material: " + name)
        material_loading = False

    # only continue if loading was successful
    if(material_loading):
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
        material_output_node.location = (300,0)

        # create mix shader node and link it to the material output
        mix_shader_node = nodes.new('ShaderNodeMixShader')
        mix_shader_node.location = (100,0)
        links.new(mix_shader_node.outputs['Shader'], material_output_node.inputs['Surface'])

        # create transparent bsdf node and link it to the mix shader node
        transparent_bsdf_node = nodes.new('ShaderNodeBsdfTransparent')
        transparent_bsdf_node.location = (-200, 100)
        links.new(transparent_bsdf_node.outputs['BSDF'], mix_shader_node.inputs[1]) # first 'Shader' input

        # create principled bsdf node and link it to the material output
        principled_bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
        principled_bsdf_node.location = (-200,0)
        principled_bsdf_node.width = 200
        links.new(principled_bsdf_node.outputs['BSDF'], mix_shader_node.inputs[2]) # second 'Shader' input

        # create texture input nodes and link them to the correct place
        counter = 0
        for maptype, mapname in material_file.mapinfo.items():
            texture_image = None

            try:
                texture_image = bpy.data.images[mapname]
            except:
                try:
                    texture_image = bpy.data.images.load(texture_fpath + mapname + '.dds', True)
                except:
                    texture = TEXTUREREADER.Texture()
                    if(texture.load_texture(texture_fpath + mapname + '.iwi')):
                        texture_image = bpy.data.images.new(mapname, texture.width, texture.height)
                        pixels = [x / 255 for x in texture.texture_data]
                        texture_image.pixels = pixels
                    else:
                        print("Couldn't find/load " + mapname + " (dds/iwi). Image texture will not be created.")

            if(texture_image != None):
                # creating texture input node
                texture_node = nodes.new('ShaderNodeTexImage')
                texture_node.label = maptype
                texture_node.location = (-700, 0 - 250 * counter)
                texture_node.image = texture_image

                # linking texture input node
                if(maptype == MATERIALREADER.MTLMapTypes['colorMap']):
                    links.new(texture_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                    links.new(texture_node.outputs['Alpha'], mix_shader_node.inputs['Fac'])
                elif(maptype == MATERIALREADER.MTLMapTypes['specularMap']):
                    links.new(texture_node.outputs['Color'], principled_bsdf_node.inputs['Specular'])
                elif(maptype == MATERIALREADER.MTLMapTypes['normalMap']):
                    # create normalmap node
                    bump_node = nodes.new('ShaderNodeBump')
                    bump_node.location = (-450, -500)

                    links.new(texture_node.outputs['Color'], bump_node.inputs['Height'])
                    links.new(bump_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                elif(maptype == MATERIALREADER.MTLMapTypes['detailMap']):
                    pass

                counter += 1

        # create texture coordinate node
        textcoord_node = nodes.new('ShaderNodeTexCoord')
        textcoord_node.location = (-1000, -150)
        for node in [node for node in nodes if node.type == 'TEX_IMAGE']:
            links.new(textcoord_node.outputs['UV'], node.inputs['Vector'])
