#
# Class to extract catalog metadata from a FITS file and output it as JSON.
#   Written by: Tom Hicks. 7/6/2020.
#   Last Modified: Refactor file info gathering.
#
import os
import sys

from astropy.io import fits

import imdtk.exceptions as errors
import imdtk.core.fits_utils as fits_utils
from imdtk.core.file_utils import gather_file_info
from imdtk.tasks.i_task import IImdTask


class FitsCatalogMetadataTask (IImdTask):
    """ Class to extract catalog metadata from a FITS file and output it as JSON. """

    def __init__(self, args):
        """
        Constructor for the class to extract catalog metadata from a FITS file and output it as JSON.
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
        catalog_hdu = self.args.get('catalog_hdu', 1)

        try:
            with fits.open(fits_file) as hdus_list:
                if (not fits_utils.is_catalog_file(hdus_list)):
                    errMsg = "Skipping non-catalog FITS file '{}'".format(fits_file)
                    raise errors.UnsupportedTypeError(errMsg)

                hdrs = fits_utils.get_header_fields(hdus_list, catalog_hdu, ignore_list)
                cinfo = fits_utils.get_column_info(hdus_list, catalog_hdu)

        except OSError as oserr:
            errMsg = "Unable to read catalog metadata from FITS file '{}': {}.".format(fits_file, oserr)
            raise errors.ProcessingError(errMsg)

        metadata = dict()                   # create overall metadata structure
        finfo = gather_file_info(fits_file)
        if (finfo is not None):             # add common file information
            metadata['file_info'] = finfo
        if (hdrs is not None):              # add the headers to the metadata
            metadata['headers'] = hdrs
        if (cinfo is not None):             # add column metadata to the metadata
            metadata['column_info'] = cinfo
        return metadata                     # return the results of processing
