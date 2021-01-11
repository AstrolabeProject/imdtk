#
# Class for extracting header information from FITS files.
#   Written by: Tom Hicks. 5/23/2020.
#   Last Modified: Redo image/catalog files tests.
#
import os
import sys

from astropy.io import fits

import imdtk.exceptions as errors
import imdtk.core.fits_utils as fits_utils
from imdtk.core.file_utils import gather_file_info
from imdtk.tasks.i_task import IImdTask


class FitsImageMetadataTask (IImdTask):
    """ Class for extracting header information from FITS files. """

    def __init__(self, args):
        """
        Constructor for the class extracting header information from FITS files.
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

        # process the given, already validated FITS file
        fits_file = self.args.get('fits_file')
        ignore_list = self.args.get('ignore_list') or fits_utils.FITS_IGNORE_KEYS
        which_hdu = self.args.get('which_hdu', 0)

        try:
            with fits.open(fits_file) as hdus_list:
                if (not fits_utils.has_image_data(hdus_list)):
                    errMsg = f"Skipping FITS file '{fits_file}': no image data in primary HDU"
                    raise errors.UnsupportedType(errMsg)

                hdrs = fits_utils.get_header_fields(hdus_list, which_hdu, ignore_list)

        except OSError as oserr:
            errMsg = "Unable to read image metadata from FITS file '{}': {}.".format(fits_file, oserr)
            raise errors.ProcessingError(errMsg)

        metadata = dict()                   # create overall metadata structure
        finfo = gather_file_info(fits_file)
        if (finfo is not None):             # add common file information
            metadata['file_info'] = finfo
        if (hdrs is not None):              # add the headers to the metadata
            metadata['headers'] = hdrs
        return metadata                     # return the results of processing
