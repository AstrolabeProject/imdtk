#
# Class for extracting header information from iRods-resident FITS files.
#   Written by: Tom Hicks. 10/15/20.
#   Last Modified: Add sanity checks, error handling, and doc strings.
#
import os
import sys

# from astropy.io import fits

from irods.exception import DataObjectDoesNotExist

import imdtk.exceptions as errors
import imdtk.core.fits_irods_helper as firh
import imdtk.core.fits_utils as fits_utils

from imdtk.core.fits_utils import FITS_IGNORE_KEYS
from imdtk.tasks.i_task import IImdTask
from imdtk.tools.cli_utils import FITS_FILE_EXIT_CODE


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
        if (self.irods):
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

        ignore_list = self.args.get('ignore_list') or fits_utils.FITS_IGNORE_KEYS
        which_hdu = self.args.get('which_hdu', 0)

        # get the iRods file path of the file to be opened
        irff_path = self.args.get('irods_fits_file')

        # the specified FITS file must have a valid FITS extension
        if (not fits_utils.is_fits_filename(irff_path)):
            errMsg = "A readable, valid FITS image file must be specified.".format(irff_path)
            raise errors.ProcessingError(errMsg)

        try:
            # get an instance of the iRods accessor class
            self.irods = firh.FitsIRodsHelper(self.args)

            # get the specified FITS file
            irff = self.irods.getf(irff_path, absolute=True)

            # sanity check on given FITS file
            if (irff.size < firh.FITS_BLOCK_SIZE):
                errMsg = "File is too small to be a valid FITS file: '{}'".format(irff_path)
                raise errors.UnsupportedTypeError(errMsg)

            # TODO: skip catalog files LATER:
            # with fits.open(irff_path) as hdus_list:
            #     if (fits_utils.is_catalog_file(hdus_list)):
            #         errMsg = "Skipping FITS catalog '{}'".format(irff_path)
            #         raise errors.UnsupportedTypeError(errMsg)

            # get and save some metadata ABOUT the iRods FITS file
            file_info = self.irods.get_irods_file_info(irff)

            # now try to read the FITS header from the FITS file
            header = self.irods.read_header(irff)
            if (not header):
                errMsg = "Unable to read image metadata headers from iRods FITS file '{}'.".format(irff_path)
                raise errors.ProcessingError(errMsg)

            else:
                hdrs = fits_utils.get_fields_from_header(header)

        except DataObjectDoesNotExist as dodne:
            errMsg = "Unable to find the specified iRods FITS file '{}'.".format(irff_path)
            raise errors.ProcessingError(errMsg)

        except OSError as oserr:
            errMsg = "Unable to read image metadata from iRods FITS file '{}': {}.".format(irff_path, oserr)
            raise errors.ProcessingError(errMsg)

        metadata = dict()                   # create overall metadata structure
        metadata['file_info'] = file_info   # add previously gathered remote file information
        metadata['headers'] = hdrs          # add the headers to the metadata
        return metadata                     # return the results of processing


    #
    # Non-interface and/or task-specific Methods
    #
