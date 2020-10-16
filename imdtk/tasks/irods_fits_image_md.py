#
# Class for extracting header information from iRods-resident FITS files.
#   Written by: Tom Hicks. 10/15/20.
#   Last Modified: Initial creation.
#
import os
import sys

from astropy.io import fits

import imdtk.exceptions as errors
import imdtk.core.fits_utils as fits_utils
import imdtk.core.irods_helper as irods
from imdtk.tasks.i_task import IImdTask


class IRodsFitsImageMetadataTask (IImdTask):
    """ Class for extracting header information from iRods-resident FITS files. """

    def __init__(self, args):
        """
        Constructor for the class extracting header information from iRods-resident FITS files.
        """
        super().__init__(args)


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
        irods_fits_file = self.args.get('irods_fits_file')
        # check_irods_fits_file(irods_fits_file, TOOL_NAME) # throw error if not found

        # process the validated FITS file
        ignore_list = self.args.get('ignore_list') or fits_utils.FITS_IGNORE_KEYS
        which_hdu = self.args.get('which_hdu', 0)

        try:
            # with fits.open(irods_fits_file) as hdus_list:
            #     if (fits_utils.is_catalog_file(hdus_list)):
            #         errMsg = "Skipping FITS catalog '{}'".format(irods_fits_file)
            #         raise errors.UnsupportedTypeError(errMsg)

            #     hdrs = fits_utils.get_header_fields(hdus_list, which_hdu, ignore_list)

            print("iRods FILE: {}".format(irods_fits_file)) # REMOVE LATER
            hdrs = {}                       # REMOVE LATER

            file_info = self.get_file_info(irods_fits_file) # TODO: IMPLEMENT LATER

        except OSError as oserr:
            errMsg = "Unable to read image metadata from FITS file '{}': {}.".format(irods_fits_file, oserr)
            raise errors.ProcessingError(errMsg)

        metadata = dict()                   # create overall metadata structure
        metadata['file_info'] = file_info   # add previously gathered remote file information
        metadata['headers'] = hdrs          # add the headers to the metadata
        return metadata                     # return the results of processing



    #
    # Non-interface and/or task-specific Methods
    #

    def get_file_info (self, irods_fits_file):
        """ Return a dictionary of information about the given file. """
        # TODO: really implement LATER:
        file_info = dict()
        file_info['file_path'] = irods_fits_file
        file_info['file_name'] = os.path.basename(irods_fits_file)
        # file_info['file_size'] = os.path.getsize(irods_fits_file)
        return file_info
