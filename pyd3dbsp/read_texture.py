import struct
import os
import re

from collections import namedtuple
from enum import Enum

from . import texture_decoder as DECODER

TEXTHeader = namedtuple('TEXTHeader', 
    ('magic, version,'
    'format,'
    'usage,'
    'width, height,'
    'filesize,'
    'texture_ofs, mipmap1_ofs, mipmap2_ofs')
    )
fmt_TEXTHeader = '<3sBBBHH2xIIII'

class TextureEnums(Enum):
    """
    TextureEnums class for storing some important values
    """
    MAGIC = 'IWi'
    VERSION = 5

class TextureUsage(Enum):
    """
    TextureUsage enum class to store the possible usages
    """
    Color = 0x00
    Default = 0x01
    Skybox = 0x05

class TextureFormat(Enum):
    """
    TextureFormat enum class to store the possible texture formats
    """
    ARGB32 = 0x01
    RGB24 = 0x02
    GA16 = 0x03
    A8 = 0x04
    DXT1 = 0x0B
    DXT3 = 0x0C
    DXT5 = 0x0D

class Texture():
    """
    Texture class for reading and storing data of Call of Duty 2 .iwi files.
    """

    def __init__(self):
        """
        Class constructor to initialize the class properties.

        Properties:
        -----------
        header          - namedtuple    - Header information
        texture_data    - bytes         - Raw texture data
        width           - int           - Width of the image
        height          - int           - Height of the image
        format          - TextureFormat - Format of the image
        usage           - TextureUsage  - Usage of the image
        -----------
        """
        self.header = None
        self.texture_data = None
        #self.mipmap1_data = None
        #self.mipmap2_data = None

        self.width = None
        self.height = None
        self.format = None
        self.usage = None

    def _read_header(self, file):
        """
        Read the header of the image/texture

        Parameters:
        -----------
        file - file object - File to read from
        -----------
        """
        file.seek(0)
        header_data = file.read(struct.calcsize(fmt_TEXTHeader))
        self.header = TEXTHeader._make(struct.unpack(fmt_TEXTHeader, header_data))
        self.header = self.header._replace(magic = self.header.magic.decode('utf-8'))
        
        self.width = self.header.width
        self.height = self.header.height
        self.format = self.header.format
        self.usage = self.header.usage
        

    def _read_raw_data(self, file):
        """
        Read the raw data of the image/texture

        Parameters:
        -----------
        file - file object - File to read from
        -----------
        """
        file.seek(self.header.texture_ofs, os.SEEK_SET)
        raw_data = file.read(self.header.filesize - self.header.texture_ofs)
        if(self.format == TextureFormat.DXT1.value):
            self.texture_data = DECODER.decode_dxt1(raw_data, self.width, self.height)
        elif(self.format and ( TextureFormat.DXT3.value or TextureFormat.DXT5.value )):
            self.texture_data = DECODER.decode_dxt5(raw_data, self.width, self.height)
        #TODO rest of the decoding if there is any

    def load_texture(self, filepath):
        """
        Load a Call of Duty 2 .iwi file and read all the necessary data from it

        Parameters:
        -----------
        filepath - string - Path to the file
        -----------

        Returns:
        --------
        Boolean - True/False wether the file reading was successful or not
        --------
        """
        with open(filepath, 'rb') as file:
            self._read_header(file)
            if(self.header.magic == TextureEnums.MAGIC.value and self.header.version == TextureEnums.VERSION.value):
                try:
                    self._read_raw_data(file)
                except:
                    return False

                return True
            else:
                return False
