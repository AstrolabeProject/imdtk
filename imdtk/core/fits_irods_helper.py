#
# Class for manipulating FITS files within the the iRods filesystem.
#   Written by: Tom Hicks. 11/1/20.
#   Last Modified: Refactor/simplify calculation of data segment length.
#
import os
import sys
import copy
import datetime as dt
from math import ceil

from astropy.io import fits

from imdtk.core import FitsHeaderInfo
import imdtk.core.fits_utils as fits_utils
from imdtk.core.fits_utils import FITS_IGNORE_KEYS
from imdtk.core.irods_helper import IRodsHelper
from imdtk.core.misc_utils import product


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


    def get_header_fields (self, irods_fits_file, which_hdu=0, ignore=FITS_IGNORE_KEYS):
        """
        Return a dictionary of keys and values for the cards in the selected HDU
        (default: 0 (the first HDU)) or None, if the given HDU index is out of range.
        The result dictionary will not contain entries for cards whose keys are
        in the given "ignore list". Note that the result dictionary will contain only the
        last value found for duplicate keys.
        """
        with irods_fits_file.open('r+') as irff_fd:
            header = self.get_header(irff_fd, irods_fits_file.size, which_hdu)
            if (header):
                return fits_utils.get_fields_from_header(header, ignore)
            else:
                return None


    def get_header (self, irff_fd, irff_size, which_hdu=0):
        # always have to read the primary header to start
        hdr_info = self.read_header(irff_fd, irff_size)

        hdr_index = 0
        while (hdr_index < which_hdu):
            datalen = self.calculate_data_length(hdr_info)
            pos = irff_fd.seek(datalen, 1)
            if (pos >= irff_size):          # exit condition: abort if at or past EOF
                return None                 # truncated file or no such HDU: exit out now

            hdr_info = self.read_header(irff_fd, irff_size)
            if (hdr_info is None):
                return None
            hdr_index += 1

        return hdr_info.hdr


    def calculate_data_length (self, hdr_info):
        '''
        Calculate the length of the data segment following the given header information.
        Each FITS header has enough information to predict the location of the next header.
        Calculations based on the FITS Standard version 4.0, revision 8/13/2018.
        '''
        if (hdr_info.hdr.get('NAXIS') == 0):         # FITS 4.0: 4.4.1.1
            return 0

        if (hdr_info.hdr.get('SIMPLE', False) is True):  # Primary Header
            return self.calc_primary_data_length(hdr_info.hdr)

        elif (hdr_info.hdr.get('XTENSION', None) in ['IMAGE', 'TABLE']):
            return self.calc_extension_data_length(hdr_info.hdr)

        elif (hdr_info.hdr.get('XTENSION', None) in ['BINTABLE']):
            return self.calc_extension_data_length(hdr_info.hdr, hdr_info.hdr.get('PCOUNT', 1))

        else:
            raise RuntimeError('Unrecognized XTENSION type while calculating HDU data length')


    def calc_primary_data_length (self, header):
        """
        Calculate length (in bytes) of the data segment following the (given) primary header.
        """
        if (header.get('NAXIS') == 0):      # sanity check per FITS 4.0: 4.4.1.1
            return 0
        B = fits_utils.bitpix_size(header['BITPIX']) / 8  # bits to bytes
        N = [header[f'NAXIS{idx}'] for idx in range(1, header['NAXIS'] + 1)]
        if (0 in N):                        # per FITS 4.0: 4.4.1.1
            return 0                        # zero in a NAXISn => no data blocks
        blocks = ceil(B * (product(N)) / FITS_BLOCK_SIZE)
        return (blocks * FITS_BLOCK_SIZE)


    def calc_extension_data_length (self, header, PCOUNT=0, GCOUNT=1):
        """
        Calculate length (in bytes) of the data segment following the given extension header.
        Defaults are provided for PCOUNT and GCOUNT but must be overridden by the calling
        function, where needed, as per the FITS Standard 4.0, sections 7.1, 7.2, and 7.3.
        """
        if (header.get('NAXIS') == 0):      # sanity check per FITS 4.0: 4.4.1.1
            return 0
        B = fits_utils.bitpix_size(header['BITPIX']) / 8
        N = [header[f'NAXIS{idx}'] for idx in range(1, header['NAXIS'] + 1)]
        if (0 in N):                        # per FITS 4.0: 4.4.1.1, 7.1.1
            return 0                        # zero in a NAXISn => no data blocks
        blocks = ceil(B * GCOUNT * (PCOUNT + product(N)) / FITS_BLOCK_SIZE)
        return (blocks * FITS_BLOCK_SIZE)



    def read_header (self, irff_fd, irff_size):
        """
        Read and return the FITS header from the given open file at the current offset.

        Returns the header in a header information object (FitsHeaderInfo) along with
        the header offset (from the start of the stream) and header length.

        Returns None if the file does not contain a full block of bytes from the given offset.
        """
        header_str = b''
        length = 0
        start = irff_fd.tell()              # save absolute starting offset
        pos = start                         # absolute current offset

        while True:
            if (pos >= irff_size):          # safety check: abort on empty or truncated file
                return None                 # exit out now

            block = irff_fd.read(FITS_BLOCK_SIZE)  # read next block
            header_str += block                    # append block data
            length += FITS_BLOCK_SIZE              # increment block length

            if (header_str.strip().endswith(FITS_END_KEY)):
                # make a FITS header from the collected bytes
                header = fits.Header.fromstring(header_str.decode(FITS_ENCODING))
                # return a header info object
                return FitsHeaderInfo(start, length, header)
            else:
                pos = irff_fd.tell()
