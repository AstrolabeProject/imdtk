#
# Class for manipulating FITS files within the the iRods filesystem.
#   Written by: Tom Hicks. 11/1/20.
#   Last Modified: Split iRods file metadata into file info, irods md, and content md.
#
import os
import sys
import copy
import datetime as dt
from math import ceil

from astropy.io import fits
from astropy.io.fits.hdu.hdulist import HDUList
from astropy import wcs

import imdtk.core.fits_utils as fits_utils
from imdtk.core import FitsHeaderInfo
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


    def get_column_info (self, irods_fits_file, hdu):
        """
        Return a dictionary of metadata describing the columns of the table in the
        given HDU. Per Astropy, the returned dictionary contains arrays of metadata,
        each containing values for a particular property for each table column (e.g., name,
        format, unit, bscale, etc).
        """
        col_md = None
        try:
            if (hdu is not None):
                col_md = hdu.columns.info(output=False)
        except AttributeError as ae:        # probably wrong HDU was specified
            return None
        return col_md


    def get_content_metadata (self, irff=None):
        """
        Return a dictionary of content metadata (if any) attached to the given iRods file.
        Content metadata is about the content of the file, not about the iRods file itself.
        """
        cmd = dict()

        if (irff):
            cmd = getattr(irff, 'metadata', lambda: None)
            if (cmd):
                cmd = { md.name: md.value for md in cmd.items() }

        return cmd


    def get_hdu (self, irods_fits_file, which_hdu=0):
        """
        Return the specified HDU (default: 0 (the first HDU)) of the given iRods FITS file.
        Returns None if the specified HDU is out of range.
        """
        with irods_fits_file.open('r+') as irff_fd:
            return self.get_hdu_at(irff_fd, irods_fits_file.size, which_hdu)


    def get_hdu_at (self, irff_fd, irff_size, which_hdu=0):
        """
        Follow the chain of HDU headers and return the specified HDU,
        given an open iRods FITS file and its size.
        Returns None if the specified HDU is out of range.

        Note: the current file position is moved as a side-effect of this method!
        """
        hdr_info = self.get_header_info_at(irff_fd, irff_size, which_hdu)
        if (hdr_info is None):              # failed to find the desired header
            return None                     # signal failure

        data_len = self.calc_data_length(hdr_info.hdr)  # find length of data segment
        hdu_len = hdr_info.length + data_len  # calculate total length of HDU

        irff_fd.seek(hdr_info.offset, 0)      # seek to start of HDU
        return self.read_hdu(irff_fd, irff_size, hdu_len)


    def get_header (self, irods_fits_file, which_hdu=0):
        """
        Return a FITS header for the specified HDU (default: 0 (the first HDU)) of
        the given iRods FITS file or return None, if the given HDU index is out of range.
        """
        with irods_fits_file.open('r+') as irff_fd:
            return self.get_header_at(irff_fd, irods_fits_file.size, which_hdu)


    def get_header_at (self, irff_fd, irff_size, which_hdu=0):
        """
        Follow the chain of HDU headers to return the header for
        the specified HDU, given an open iRods FITS file and its size.
        Returns None if the specified HDU is out of range.

        Note: the current file position is moved as a side-effect of this method!
        """
        hdr_info = self.get_header_info_at(irff_fd, irff_size, which_hdu)
        return hdr_info.hdr if (hdr_info is not None) else None


    def get_header_info_at (self, irff_fd, irff_size, which_hdu=0):
        """
        Follow the chain of HDU headers to return a header information record for
        the specified HDU, given an open iRods FITS file and its size.
        Returns None if the specified HDU is out of range.

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

        return hdr_info                     # success: return the desired header information


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
            # attributes common to all file info structures
            file_info['file_path'] = irff.path
            file_info['file_name'] = irff.name
            file_info['file_size'] = irff.size

        return file_info


    def get_irods_metadata (self, irff=None):
        """ Return a dictionary of metadata about the given iRods file (node) itself. """
        irmd = dict()

        if (irff):
            for attr in IRODS_FILE_ATTRIBUTES:
                val = getattr(irff, attr, lambda: None)
                if (val):
                    irmd[attr] = str(val) if (isinstance(val, dt.datetime)) else val

        return irmd


    def get_WCS (self, header):
        """
        Return a World Coordinate System structure from the given header or
        return None, if unable to get the WCS info from the given header.
        """
        return wcs.WCS(header) if (header is not None) else None


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


    def read_chunk (self, irff_fd, irff_size, chunk_size=FITS_BLOCK_SIZE):
        """
        Read and return a chunk of bytes from the given open file at the current file position.
        Returns None if the file does not contain the specified number of bytes from
        the current file position.

        Note: the current file position is moved as a side-effect of this method!
        """
        pos = irff_fd.tell()                # current position in file
        if ((pos + chunk_size) > irff_size):  # not enough data left to read
            return None                     # signal failure
        return irff_fd.read(chunk_size)     # read and return chunck


    def read_hdu (self, irff_fd, irff_size, hdu_size):
        """
        Read a chunk of hdu_size bytes at the current file position and
        return a single HDU, given an open iRods FITS file and its size.
        Returns None if the unable to produce an HDU.

        Note: the current file position is moved as a side-effect of this method!
        """
        hdu_data = self.read_chunk(irff_fd, irff_size, chunk_size=hdu_size)
        if (hdu_data is None):
            return None                     # signal failure

        # create singleton list of HDU from the HDU data bytes
        hdulist = HDUList.fromstring(hdu_data)
        if (hdulist and len(hdulist) > 0):
            return hdulist[0]               # return the solitary HDU
        else:                               # just in case
            return None                     # signal failure


    def read_header (self, irff_fd, irff_size):
        """
        Read and return the FITS header from the given open file at the current file position.

        Returns the header in a header information object (FitsHeaderInfo) along with
        the header offset (from the start of the stream) and header length.

        Returns None if the file does not contain a full block of bytes from
        the current file position.

        Note: the current file position is moved as a side-effect of this method!
        """
        header_str = b''
        length = 0
        start = irff_fd.tell()              # save absolute starting position
        pos = start                         # absolute current position

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
