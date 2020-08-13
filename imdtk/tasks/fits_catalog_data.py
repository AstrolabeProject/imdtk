#
# Class to extract a catalog data table from a FITS file and output it as JSON.
#   Written by: Tom Hicks. 8/12/2020.
#   Last Modified: Minor clarification to doc string.
#
import os
import sys

from astropy.io import fits
from numpyencoder import NumpyEncoder

import imdtk.exceptions as errors
import imdtk.core.fits_utils as fits_utils
from imdtk.tasks.i_task import IImdTask


class FitsCatalogDataTask (IImdTask):
    """ Class to extract a catalog data table from a FITS file and output it as JSON. """

    def __init__(self, args):
        """
        Constructor for the class to a extract catalog data table from a FITS file and output it as JSON.
        """
        super().__init__(args)

        # Path to a readable FITS catalog file
        self._fits_file = args.get('fits_file')


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
        table_hdu = self.args.get('table_hdu', 1)

        try:
            with fits.open(fits_file) as hdus_list:
                if (not fits_utils.is_catalog_file(hdus_list)):
                    errMsg = "Skipping non-catalog FITS file '{}'".format(fits_file)
                    raise errors.UnsupportedTypeError(errMsg)
                hdrs = fits_utils.get_header_fields(hdus_list, table_hdu, ignore_list)
                cinfo = fits_utils.get_column_info(hdus_list, table_hdu)

                table = hdus_list[table_hdu].data
                meta = fits_utils.get_table_meta_attribute(table)
                data = fits_utils.read_data(table)

        except OSError as oserr:
            errMsg = "Unable to read catalog data from FITS file '{}': {}.".format(fits_file, oserr)
            raise errors.ProcessingError(errMsg)

        outdata = self.make_context()       # create overall metadata output structure
        outdata['headers'] = hdrs           # add the headers to the output
        outdata['meta'] = meta              # add extra table metadata to the output
        outdata['column_info'] = cinfo      # add column metadata to the output
        outdata['data'] = data              # add the data table to the output
        return outdata                      # return the results of processing


    def output_JSON (self, outdata, file_path=None, **json_keywords):
        """
        Override this method to add the numpy encoder class needed to
        serialize astropy.io.fits.fitsrec.FITS_rec data (aka numpy recarray).
        """
        super().output_JSON(outdata, file_path=file_path, cls=NumpyEncoder)



    #
    # Non-interface and/or task-specific Methods
    #

    def add_file_info (self, results):
        """ Add information about the input file to the given results map. """
        file_info = dict()
        fits_file = self.args.get('fits_file')
        file_info['file_name'] = os.path.basename(fits_file)
        file_info['file_path'] = os.path.abspath(fits_file)
        file_info['file_size'] = os.path.getsize(fits_file)
        results['file_info'] = file_info


    def make_context (self):
        """
        Create the larger structure which holds the various information sections.
        Start with file information.
        """
        results = dict()
        self.add_file_info(results)
        return results
