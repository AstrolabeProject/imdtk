#
# Class for manipulating FITS files within the the iRods filesystem.
#   Written by: Tom Hicks. 11/1/20.
#   Last Modified: Add is_image_header method.
#
import os
import sys
import copy
import datetime as dt
from math import ceil

from astropy.io import fits

from imdtk.core import FitsHeaderInfo
import imdtk.core.fits_utils as fits_utils
from imdtk.core.fits_utils import FITS_BLOCK_SIZE, FITS_END_KEY, FITS_IGNORE_KEYS
from imdtk.core.irods_helper import IRodsHelper
from imdtk.core.misc_utils import product


FITS_ENCODING = 'utf-8'
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


    def calculate_data_length (self, header):
        '''
        Calculate the length of the data segment following the given header information.
        Each FITS header has enough information to predict the location of the next header.
        Calculations based on the FITS Standard version 4.0, revision 8/13/2018.
        '''
        if (header.get('NAXIS') == 0):         # FITS 4.0: 4.4.1.1
            return 0

        if (header.get('SIMPLE', False) is True):  # Primary Header
            return self.calc_data_length(header, primary=True)

        elif (header.get('XTENSION', None) in ['IMAGE', 'TABLE']):
            return self.calc_data_length(header)

        elif (header.get('XTENSION', None) in ['BINTABLE']):
            return self.calc_data_length(header, PCOUNT=header.get('PCOUNT', 1))

        else:
            raise RuntimeError('Unrecognized XTENSION type while calculating HDU data length')


    def calc_data_length (self, header, GCOUNT=1, PCOUNT=0, primary=False):
        """
        Calculate the length (in bytes) of the data segment following the given header.
        Defaults are provided for PCOUNT and GCOUNT but must be overridden by the calling
        function, where needed, as per the FITS Standard 4.0, section 7.1.
        PCOUNT and GCOUNT are not used by the Primary header, as per section 4.4.1.
        """
        if (header.get('NAXIS') == 0):      # sanity check per FITS 4.0: section 4.4.1.1
            return 0

        B = fits_utils.bitpix_size(header['BITPIX']) / 8
        N = [header[f'NAXIS{idx}'] for idx in range(1, header['NAXIS'] + 1)]

        if (0 in N):                        # per FITS 4.0: 4.4.1.1, 7.1.1
            return 0                        # zero in any NAXISn => no data blocks

        if (primary):                       # if this is the primary header
            blocks = ceil(B * (product(N)) / FITS_BLOCK_SIZE)
        else:                               # else this is an extension header
            blocks = ceil(B * GCOUNT * (PCOUNT + product(N)) / FITS_BLOCK_SIZE)

        return (blocks * FITS_BLOCK_SIZE)


    def get_header (self, irods_fits_file, which_hdu=0):
        """
        Return a FITS header for the specified HDU (default: 0 (the first HDU)) of
        the given iRods FITS file or return None, if the given HDU index is out of range.
        """
        with irods_fits_file.open('r+') as irff_fd:
            return self.get_header_at(irff_fd, irods_fits_file.size, which_hdu)


    def get_header_at (self, irff_fd, irff_size, which_hdu=0):
        """
        Follow the chain of HDU headers to return the header for the specified
        HDU, given an open iRods FITS file and its size.

        Note: the current file position is moved as a side-effect of this method!
        """
        # always have to read the primary header to start
        irff_fd.seek(0, 0)                  # move to beginning of file
        hdr_info = self.read_header(irff_fd, irff_size)
        if (hdr_info is None):              # if unable to read first header
            return None                     # signal failure

        hdr_index = 0                       # just read primary header
        while (hdr_index < which_hdu):
            datalen = self.calculate_data_length(hdr_info.hdr)
            pos = irff_fd.seek(datalen, 1)  # skip over data segment
            if (pos >= irff_size):          # exit condition: abort if at or past EOF
                return None                 # exits on truncated file or no such HDU

            hdr_info = self.read_header(irff_fd, irff_size)  # try to read next header
            if (hdr_info is None):          # if unable to read a header at current position
                return None                 # signal failure
            else:                           # else we got another header
                hdr_index += 1

        return hdr_info.hdr                 # success: return the desired header


    def get_header_fields (self, irods_fits_file, which_hdu=0, ignore=FITS_IGNORE_KEYS):
        """
        Return a dictionary of keys and values for the cards in the selected HDU
        (default: 0 (the first HDU)) or None, if the given HDU index is out of range.
        The result dictionary will not contain entries for cards whose keys are
        in the given "ignore list". Note that the result dictionary will contain only the
        last value found for duplicate keys.
        """
        header = self.get_header(irods_fits_file, which_hdu)
        if (header):
            return fits_utils.get_fields_from_header(header, ignore)
        else:
            return None


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
        """ Return a dictionary of iRods file metadata (if any) FOR the given iRods file. """
        metadata = dict()

        if (irff):
            irmd = getattr(irff, 'metadata', lambda: None)
            if (irmd):
                metadata = { md.name: md.value for md in irmd.items() }

        return metadata


    def is_catalog_header (self, header):
        """
        Tell whether the given FITS HDU header is for a catalog or not.
        Assumes: a catalog HDU will be of type BINTABLE or TABLE:
        """
        if (header is not None):
            return (header.get('XTENSION') in ['BINTABLE', 'TABLE'])
        else:
            return False


    def is_image_header (self, header):
        """
        Tell whether the given FITS HDU header is for an image or not.
        Note: based on a bunch of heuristics, hopefully correctly inferred from
              the FITS Standard version 4.0, revision 8/13/2018.
        """
        if ((header is None) or (header.get('NAXIS') == 0)):  # per FITS 4.0: 4.4.1.1
            return False

        # if this header is the Primary Header
        if (header.get('SIMPLE', False) is True):
            if (header.get('NAXIS') < 2):   # heuristic: images have at least 2 dimensions?
                return False

            N = [header[f'NAXIS{idx}'] for idx in range(1, header['NAXIS'] + 1)]
            if (0 in N):                    # per FITS 4.0: 4.4.1.1, 7.1.1
                return False                # zero in any NAXISn => no data blocks

            if (header.get('NTABLE') is not None):  # heuristic: number of table extensions
                return False

            if (header.get('VOTMETA', False) is True):  # heuristic
                return False

            return True                     # passed all checks

        # else if this header is an Image Extension header
        elif (header.get('XTENSION') in ['IMAGE']):
            if (header.get('NAXIS') < 2):   # heuristic: images have at least 2 dimensions?
                return False

            N = [header[f'NAXIS{idx}'] for idx in range(1, header['NAXIS'] + 1)]
            if (0 in N):                    # per FITS 4.0: 4.4.1.1, 7.1.1
                return False                # zero in any NAXISn => no data blocks

            return True                     # passed all checks

        else:                               # else assume not an image header
            return False


    def read_header (self, irff_fd, irff_size):
        """
        Read and return the FITS header from the given open file at the current offset.

        Returns the header in a header information object (FitsHeaderInfo) along with
        the header offset (from the start of the stream) and header length.

        Returns None if the file does not contain a full block of bytes from the given offset.

        Note: the current file position is moved as a side-effect of this method!
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
