import struct
import os

def read_nullstr(file):
    string = b''
    character = None
    while(character != b'\x00'):
        character = file.read(1)
        string += character
    string = string.decode('utf-8').rstrip('\x00')
    return string

def return_filename_from_filepath(filepath):
    head, tail = os.path.split(filepath)
    return tail or os.path.basename(head)

def file_not_found(filepath, msg):
    filename = return_filename_from_filepath(filepath)
    print(filename + " " + str(msg))