#
# Class for extracting header information from iRods-resident FITS files.
#   Written by: Tom Hicks. 10/15/20.
#   Last Modified: Refactor for new FITS iRods helper class.
#
import os
import sys

# from astropy.io import fits

import imdtk.exceptions as errors
import imdtk.core.fits_irods_helper as firh
import imdtk.core.fits_utils as fits_utils

from imdtk.core.fits_utils import FITS_IGNORE_KEYS
from imdtk.tasks.i_task import IImdTask


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
        irff_path = self.args.get('irods_fits_file')
        # check_irods_fits_file(irff_path, TOOL_NAME) # throw error if not found

        # process the validated FITS file
        ignore_list = self.args.get('ignore_list') or fits_utils.FITS_IGNORE_KEYS
        which_hdu = self.args.get('which_hdu', 0)

        try:
            # TODO: skip catalog files LATER:
            # with fits.open(irff_path) as hdus_list:
            #     if (fits_utils.is_catalog_file(hdus_list)):
            #         errMsg = "Skipping FITS catalog '{}'".format(irff_path)
            #         raise errors.UnsupportedTypeError(errMsg)


            self.irods = firh.FitsIRodsHelper(self.args)

            irff = self.irods.getf(irff_path, absolute=True)

            file_info = self.irods.get_irods_file_info(irff)

            header = self.irods.read_header(irff)
            hdrs = fits_utils.get_fields_from_header(header)

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
