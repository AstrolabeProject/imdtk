#
# Class for manipulating FITS files within the the iRods filesystem.
#   Written by: Tom Hicks. 11/1/20.
#   Last Modified: WIP: simplify navigation within FITS file.
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
        # print("hdr_info[0]={}".format(hdr_info.hdr), file=sys.stderr) # REMOVE LATER

        hdr_index = 0
        while (hdr_index < which_hdu):
            datalen = self.calc_data_length(hdr_info)
            pos = irff_fd.seek(datalen, 1)
            if (pos >= irff_size):          # exit condition: abort if at or past EOF
                return None                 # truncated file or no such HDU: exit out now

            hdr_info = self.read_header(irff_fd, irff_size)
            if (hdr_info is None):
                return None
            # print("hdr_info[{}]={}".format(hdr_index, hdr_info), file=sys.stderr) # REMOVE LATER
            hdr_index += 1

        return hdr_info.hdr


    def calc_data_length (self, hdr_info):
        '''
        Each FITS XTENSION has enough information to predict the next location of
        the next XTENSION header. Here we'll take in the offset and length and
        return a new offset which includes the data length difference.
        '''
        if (hdr_info.hdr.get('SIMPLE', False) is True):  # Primary Header
            if (hdr_info.hdr.get('NAXIS') == 0):         # FITS Standard_4: 4.4.1.1
                return 0
            else:
                B = fits_utils.bitpix_size(hdr_info.hdr['BITPIX']) / 8  # bits to bytes
                N = [hdr_info.hdr[f'NAXIS{idx}'] for idx in range(1, hdr_info.hdr['NAXIS'] + 1)]
                # print("FNHO: */N={}, N={}".format(product(N), N), file=sys.stderr) # REMOVE LATER
                blocks = ceil((product(N) * B) / FITS_BLOCK_SIZE)
                # print("FNHO: blocks={}".format(blocks), file=sys.stderr) # REMOVE LATER
                length = (blocks * FITS_BLOCK_SIZE)
                # print("FNHO: length={}".format(length), file=sys.stderr) # REMOVE LATER
                return length

        elif (hdr_info.hdr.get('XTENSION', None) in ['IMAGE']):
            # https://ui.adsabs.harvard.edu/abs/1994A%26AS..105...53P/abstract
            # http://articles.adsabs.harvard.edu/pdf/1994A%26AS..105...53P
            B = fits_utils.bitpix_size(hdr_info.hdr['BITPIX'])
            G = hdr_info.hdr['GCOUNT']
            P = hdr_info.hdr['PCOUNT']
            N = [hdr_info.hdr[f'NAXIS{idx}'] for idx in range(1, hdr_info.hdr['NAXIS'] + 1)]
            print("FNHO: B={}, G={}, P={}, N={}".format(B, G, P, N)) # REMOVE LATER
            S = B * G * (P + product(N))
            print("FNHO: S={}".format(S)) # REMOVE LATER
            return int(S / FITS_BLOCK_SIZE) * FITS_BLOCK_SIZE

        elif (hdr_info.hdr.get('XTENSION', None) in ['BINTABLE']):
            # NAXIS1 = number of elements per row
            # NAXIS2 = number of rows in the table
            B = fits_utils.bitpix_size(hdr_info.hdr['BITPIX']) / 8  # bits to bytes
            N = hdr_info.hdr['NAXIS1'] * hdr_info.hdr['NAXIS2']
            # print("FNHO: N={}".format(N), file=sys.stderr) # REMOVE LATER
            blocks = (ceil(N * B) / FITS_BLOCK_SIZE)
            # print("FNHO: blocks={}".format(blocks), file=sys.stderr) # REMOVE LATER
            length = (blocks * FITS_BLOCK_SIZE)
            # print("FNHO: length={}".format(length), file=sys.stderr) # REMOVE LATER
            return length

        elif (hdr_info.hdr.get('XTENSION', None) in ['TABLE']):
            raise NotImplementedError('TABLE')

        else:
            raise RuntimeError('Unrecognized XTENSION type while seeking extension header')


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
