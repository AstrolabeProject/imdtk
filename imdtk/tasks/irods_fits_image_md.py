#
# Class for extracting header information from iRods-resident FITS files.
#   Written by: Tom Hicks. 10/15/20.
#   Last Modified: Continue developing: method to read first HDU headers.
#
import os
import sys

from astropy.io import fits

import imdtk.exceptions as errors
import imdtk.core.fits_utils as fits_utils
import imdtk.core.irods_helper as irh
from imdtk.core.fits_utils import FITS_IGNORE_KEYS
from imdtk.tasks.i_task import IImdTask


FITS_BLOCK_SIZE = 2880
FITS_ENCODING = 'utf-8'
FITS_END_KEY = b'END'
# FITS_END_CARD = FITS_END_KEY + ' ' * 77


class IRodsFitsImageMetadataTask (IImdTask):
    """ Class for extracting header information from iRods-resident FITS files. """

    def __init__(self, args):
        """
        Constructor for the class extracting header information from iRods-resident FITS files.
        """
        super().__init__(args)
        self.irods = None                   # holder for IRodsHelper instance


    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for the task instance. """
        self.irods.cleanup()
        super().cleanup


    #
    # Methods overriding IImdTask interface methods
    #

    def process (self, _):
        """
        Perform the main work of the task and return the results as a Python data structure.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # TODO: add check of given iRods FITS file path LATER?
        iff_path = self.args.get('irods_fits_file')
        # check_irods_fits_file(iff_path, TOOL_NAME) # throw error if not found

        # process the validated FITS file
        ignore_list = self.args.get('ignore_list') or fits_utils.FITS_IGNORE_KEYS
        which_hdu = self.args.get('which_hdu', 0)

        try:
            # with fits.open(iff_path) as hdus_list:
            #     if (fits_utils.is_catalog_file(hdus_list)):
            #         errMsg = "Skipping FITS catalog '{}'".format(iff_path)
            #         raise errors.UnsupportedTypeError(errMsg)

            #     hdrs = fits_utils.get_header_fields(hdus_list, which_hdu, ignore_list)

            hdrs = {}                       # REMOVE LATER
            print("iRods file path: {}".format(iff_path)) # REMOVE LATER

            self.irods = irh.IRodsHelper(self.args)

            print("({}.process): cwd={}".format(self.TOOL_NAME, self.irods.cwd()), file=sys.stderr)

            i_file = self.irods.getf(iff_path, absolute=True)
            print("({}.process): iRods file={}".format(self.TOOL_NAME, i_file), file=sys.stderr)

            # print([x for x in dir(i_file)], file=sys.stderr)  # for DEBUGGING

            file_info = self.get_file_info(iff_path, i_file)

            header = self.read_header(i_file)
            hdrs = fits_utils.get_fields_from_header(header)

        except OSError as oserr:
            errMsg = "Unable to read image metadata from FITS file '{}': {}.".format(iff_path, oserr)
            raise errors.ProcessingError(errMsg)

        metadata = dict()                   # create overall metadata structure
        metadata['file_info'] = file_info   # add previously gathered remote file information
        metadata['headers'] = hdrs          # add the headers to the metadata
        return metadata                     # return the results of processing



    #
    # Non-interface and/or task-specific Methods
    #

    def get_file_info (self, iff_path, i_file=None):
        """
        Return a dictionary of information about the file at the given iRods path. If given,
        use the open iRods file to get additional information.
        """
        file_info = dict()
        file_info['file_path'] = iff_path
        file_info['file_name'] = os.path.basename(iff_path)
        if (i_file):
            file_info['file_size'] = i_file.size
        return file_info


    def read_header (self, i_file):
        header_str = b''
        offset = 0

        with i_file.open('r+') as irff:
            while True:
                irff.seek(offset, 0)
                block = irff.read(FITS_BLOCK_SIZE)
                header_str += block

                if (header_str.strip().endswith(FITS_END_KEY)):
                    break
                else:
                    offset = offset + FITS_BLOCK_SIZE

        header = fits.Header.fromstring(header_str.decode(FITS_ENCODING))
        # print("HEADER={}".format(header), sile=sys.stderr)   # for DEBUGGING
        return header
