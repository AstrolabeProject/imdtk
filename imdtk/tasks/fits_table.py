#
# Class to extract an image table from a FITS file and output it as JSON.
#   Written by: Tom Hicks. 7/6/2020.
#   Last Modified: Add column information (metadata) to the returned metadata.
#
import logging as log
import os
import sys

from astropy.io import fits

import imdtk.core.fits_utils as fits_utils
from imdtk.tasks.i_task import IImdTask, STDOUT_NAME
# import imdtk.tasks.metadata_utils as md_utils


class FitsTableSourceTask (IImdTask):
    """ Class to extract an image table from a FITS file and output it as JSON. """

    def __init__(self, args):
        """
        Constructor for the class to extract an image table from a FITS file and output it as JSON.
        """
        super().__init__(args)

        # Path to a readable FITS image file from which to extract metadata.
        self._fits_file = args.get('fits_file')


    #
    # Concrete methods implementing ITask abstract methods
    #

    def process (self, _):
        """
        Perform the main work of the task and return the results as a Python data structure.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # process the given, already validated FITS file
        fits_file = self.args.get('fits_file')
        if (self._VERBOSE):
            print("({}): Processing FITS file '{}'".format(self.TOOL_NAME, fits_file), file=sys.stderr)

        ignore_list = self.args.get('ignore_list')
        table_hdu = self.args.get('table_hdu', 1)

        try:
            with fits.open(fits_file) as hdus_list:
                cinfo = fits_utils.get_column_info(hdus_list, table_hdu)
                if (ignore_list):
                    hdrs = fits_utils.get_header_fields(hdus_list, table_hdu, ignore_list)
                else:
                    hdrs = fits_utils.get_header_fields(hdus_list, table_hdu)

            if (hdrs is None):
                errMsg = "({}.process): Unable to read table metadata from FITS file '{}'.".format(self.TOOL_NAME, fits_file)
                log.error(errMsg)
                raise RuntimeError(errMsg)

            metadata = self.make_context()    # create overall metadata structure
            metadata['headers'] = hdrs        # add the headers to the metadata
            metadata['column_info'] = cinfo   # add column metadata to the metadata
            return metadata                   # return the results of processing

        except Exception as ex:
            errMsg = "({}.process): Exception while reading from FITS file '{}': {}.".format(self.TOOL_NAME, fits_file, ex)
            log.error(errMsg)
            raise RuntimeError(errMsg)


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