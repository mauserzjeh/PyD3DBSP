import struct
import os
import math

import bpy

def read_nullstr(file):
    """
    Read a null terminated string

    Parameters:
    -----------
    file - file object - File to read from
    -----------

    Returns:
    -----------
    Null terminated string
    -----------
    """
    string = b''
    character = None
    while(character != b'\x00'):
        character = file.read(1)
        string += character
    string = string.decode('utf-8').rstrip('\x00')
    return string

def return_filename_from_filepath(filepath, include_extension=True):
    """
    Return filename from the full filepath

    Parameters:
    -----------
    filepath          - string  - Full filepath
    include_extension - boolean - Whether to include extension in the returned filename or not
    -----------

    Returns:
    -----------
    -----------
    """
    head, tail = os.path.split(filepath)
    if(include_extension):
      return tail or os.path.basename(head)
    else:
      return os.path.splitext(tail)[0] or os.path.splitext(os.path.basename(head))[0]

def file_not_found(filepath, msg):
    """
    A basic function to print out a "file not found" message

    Parameters:
    -----------
    filepath - string - Full filepath
    msg      - string - Message
    -----------
    """
    filename = return_filename_from_filepath(filepath)
    print(filename + " " + str(msg))

def clean_materials():
    """
    A function to delete all existing materials
    """
    if(len(bpy.data.materials)):
      for bpy_material in bpy.data.materials:
        bpy_material.user_clear()
        bpy.data.materials.remove(bpy_material)