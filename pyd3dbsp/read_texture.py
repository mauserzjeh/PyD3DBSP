import struct
import os
import re

from collections import namedtuple
from enum import Enum

TEXTHeader = namedtuple('TEXTHeader', 
    ('magic, version,'
    'format,'
    'usage,'
    'width, height,'
    'filesize,'
    'texture_ofs, mipmap1_ofs, mipmap2_ofs')
    )
fmt_TEXTHeader = '<3sBccHH2xIIII'

class TextureUsage(Enum):
    Color = b'\x00'
    Default = b'\x01'
    Skybox = b'\x05'

class TextureFormat(Enum):
    ARGB32 = b'\x01'
    RGB24 = b'\x02'
    GA16 = b'\x03'
    A8 = b'\x04'
    DXT1 = b'\x0B'
    DXT3 = b'\x0C'
    DXT5 = b'\x0D'

class Texture():

    def __init__(self):
        self.header = None
        self.raw_texture_data = []
        self.raw_mipmap1_data = None
        self.raw_mipmap2_data = None

    def _read_header(self, file):
        file.seek(0)
        header_data = file.read(struct.calcsize(fmt_TEXTHeader))
        self.header = TEXTHeader._make(struct.unpack(fmt_TEXTHeader, header_data))
        self.header = self.header._replace(magic = self.header.magic.decode('utf-8'))

    def _read_raw_data(self, file):
        file.seek(self.header.texture_ofs, os.SEEK_SET)
        for i in range(0, (self.header.filesize - self.header.texture_ofs)):
            _byte = file.read(1)
            self.raw_texture_data.append(_byte)

    def load_texture(self, filepath):
        with open(filepath, 'rb') as file:
            self._read_header(file)
            self._read_raw_data(file)