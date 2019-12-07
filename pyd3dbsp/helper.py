import struct
import os
import math

import bpy

def read_nullstr(file):
    string = b''
    character = None
    while(character != b'\x00'):
        character = file.read(1)
        string += character
    string = string.decode('utf-8').rstrip('\x00')
    return string

def return_filename_from_filepath(filepath, include_extension=True):
    head, tail = os.path.split(filepath)
    if(include_extension):
      return tail or os.path.basename(head)
    else:
      return os.path.splitext(tail)[0] or os.path.splitext(os.path.basename(head))[0]

def file_not_found(filepath, msg):
    filename = return_filename_from_filepath(filepath)
    print(filename + " " + str(msg))

def clean_materials():
    if(len(bpy.data.materials)):
      for bpy_material in bpy.data.materials:
        bpy_material.user_clear()
        bpy.data.materials.remove(bpy_material)