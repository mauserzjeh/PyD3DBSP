import struct

def read_nullstr(file):
    string = b''
    character = None
    while(character != b'\x00'):
        character = file.read(1)
        string += character
    string = string.decode('utf-8').rstrip('\x00')
    return string