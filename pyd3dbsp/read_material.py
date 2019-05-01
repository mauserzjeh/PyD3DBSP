import struct
import os
import re

from collections import namedtuple
from enum import Enum

MTLHeader = namedtuple('MTLHeader',
    ('mtl_name_ofs, colormap_name_ofs,'
    'unk1_2Csize,'
    'mapinfoblock_number, stringinfoblock_number,'
    'mtl_type_ofs,'
    'mapinfoblock_ofs,'
    'unk2_DWORDsize,'
    'stringinfoblock_ofs')
    )
fmt_MTLHeader = '<II44sHHIIII'

"""
in case of colormap
name offset -> type offset = mapname
type offset -> next type offset = maptype string

in every other case
type offset -> name offset = maptype string
name offset -> next type offset = mapname

"""
MTLMapInfoBlock = namedtuple('MTLMapInfoBlock',
    ('type_ofs,'
    'unk1, unk2, unk3, unk4,'
    'name_ofs')
    )
fmt_MTLMapInfoBlock = '<I4bI'

MTLStringInfoBlock = namedtuple('MTLStringInfoBlock',
    ('type_ofs,'
    'unkf1, unkf2, unkf3, unkf4')
    )
fmt_MTLStringInfoBlock = '<i4f'

class MTL:

    def __init__(self):
        self.header = None
        self.mapinfoblocks = []
        self.stringinfoblocks = []

    def _read_header(self, file):
        file.seek(0)
        header_data = file.read(struct.calcsize(fmt_MTLHeader))
        self.header = MTLHeader._make(struct.unpack(fmt_MTLHeader, header_data))

    def _read_mapinfoblocks(self, file):
        file.seek(self.header.mapinfoblock_ofs, os.SEEK_SET)
        for i in range(0, self.header.mapinfoblock_number):
            mapinfoblock_data = file.read(struct.calcsize(fmt_MTLMapInfoBlock))
            mapinfoblock = MTLMapInfoBlock._make(struct.unpack(fmt_MTLMapInfoBlock, mapinfoblock_data))
            self.mapinfoblocks.append(mapinfoblock)

    def _read_stringinfoblocks(self, file):
        file.seek(self.header.stringinfoblock_ofs, os.SEEK_SET)
        for i in range(0, self.header.stringinfoblock_number):
            stringinfoblock_data = file.read(struct.calcsize(fmt_MTLStringInfoBlock))
            stringinfoblock = MTLStringInfoBlock._make(struct.unpack(fmt_MTLStringInfoBlock, stringinfoblock_data))
            self.stringinfoblocks.append(stringinfoblock)

    def load_material(self, filepath):
        with open(filepath, 'rb') as file:
            self._read_header(file)
            self._read_mapinfoblocks(file)
            self._read_stringinfoblocks(file)
