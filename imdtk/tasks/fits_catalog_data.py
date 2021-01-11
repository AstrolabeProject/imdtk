#
# Class to extract a catalog data table from a FITS file and output it as JSON.
#   Written by: Tom Hicks. 8/12/2020.
#   Last Modified: Redo image/catalog files tests.
#
import os
import sys

from astropy.io import fits
from astropy.table import Table

import imdtk.exceptions as errors
import imdtk.core.fits_utils as fits_utils
from imdtk.core.file_utils import gather_file_info
from imdtk.tasks.i_task import IImdTask


class FitsCatalogDataTask (IImdTask):
    """ Class to extract a catalog data table from a FITS file and output it as JSON. """

    def __init__(self, args):
        """
        Constructor for the class to a extract catalog data table from a FITS file and output it as JSON.
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
                if (not fits_utils.has_catalog_data(hdus_list)):
                    errMsg = f"Skipping FITS file '{fits_file}': no catalog in HDU 1"
                    raise errors.UnsupportedType(errMsg)
                hdrs = fits_utils.get_header_fields(hdus_list, catalog_hdu, ignore_list)
                cinfo = fits_utils.get_column_info(hdus_list, catalog_hdu)

                fits_rec = hdus_list[catalog_hdu].data
                data = fits_utils.rows_from_data(fits_rec)
                table = Table.read(hdus_list, hdu=catalog_hdu)
                meta = fits_utils.get_table_meta_attribute(table)

        except OSError as oserr:
            errMsg = "Unable to read catalog data from FITS file '{}': {}.".format(fits_file, oserr)
            raise errors.ProcessingError(errMsg)

        outdata = dict()                    # create overall ouput structure
        finfo = gather_file_info(fits_file)
        if (finfo is not None):             # add common file information
            outdata['file_info'] = finfo
        if (hdrs is not None):              # add the headers to the output
            outdata['headers'] = hdrs
        if (cinfo is not None):             # add column metadata to the output
            outdata['column_info'] = cinfo
        outdata['meta'] = meta              # add extra table metadata to the output
        outdata['data'] = data              # add the data table to the output

        return outdata                     # return the results of processing
