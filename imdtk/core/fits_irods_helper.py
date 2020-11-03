#
# Class for manipulating FITS files within the the iRods filesystem.
#   Written by: Tom Hicks. 11/1/20.
#   Last Modified: Add sanity checks while looping to read FITS headers.
#
import os
import sys
import copy
import datetime as dt

from astropy.io import fits

# import imdtk.core.fits_utils as fits_utils
from imdtk.core import Metadatum
from imdtk.core.irods_helper import IRodsHelper


FITS_BLOCK_SIZE = 2880
FITS_ENCODING = 'utf-8'
FITS_END_KEY = b'END'
IRODS_FILE_ATTRIBUTES =[ 'checksum', 'create_time', 'modify_time', 'name',
                         'owner_name', 'owner_zone', 'path', 'size',
                         'status', 'type', 'version' ]


class FitsIRodsHelper (IRodsHelper):
    """ Class for working with FITS files within the the iRods filesystem. """

    def __init__ (self, args={}, connect=True):
        """
        Constructor of class for manipulating FITS files within the the iRods filesystem.
        """
        super().__init__(args, connect)


    def get_irods_file_info (self, irff=None):
        """ Return a dictionary of file information about the given iRods FITS file. """
        file_info = dict()

        if (irff):
            file_info['file_path'] = irff.path
            file_info['file_name'] = irff.name
            file_info['file_size'] = irff.size
            for attr in IRODS_FILE_ATTRIBUTES:
                val = getattr(irff, attr, lambda: None)
                if (val):
                    file_info[attr] = str(val) if (isinstance(val, dt.datetime)) else val

            md = self.get_irods_file_metadata(irff)
            if (md):
                file_info['irods_metadata'] = md

        return file_info


    def get_irods_file_metadata (self, irff=None):
        """ Return a dictionary of iRods file metadata (if any) for the given iRods file. """
        metadata = dict()

        if (irff):
            irmd = getattr(irff, 'metadata', lambda: None)
            if (irmd):
                metadata = { md.name: md.value for md in irmd.items() }

        return metadata


    def read_header (self, irods_fits_file):
        if (irods_fits_file.size < FITS_BLOCK_SIZE):
            return None

        file_size = irods_fits_file.size
        header_str = b''
        offset = 0

        with irods_fits_file.open('r+') as irff_fd:
            while True:
                pos = irff_fd.seek(offset, 0)
                if (pos > file_size):       # sanity check: abort on bad file
                    return None             # exit out now

                block = irff_fd.read(FITS_BLOCK_SIZE)
                header_str += block

                if (header_str.strip().endswith(FITS_END_KEY)):
                    break
                else:
                    offset = offset + FITS_BLOCK_SIZE

        header = fits.Header.fromstring(header_str.decode(FITS_ENCODING))
        return header
