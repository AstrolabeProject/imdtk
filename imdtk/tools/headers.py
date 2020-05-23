#
# Class for extracting header information from FITS files.
#   Written by: Tom Hicks. 5/23/2020.
#   Last Modified: Initial creation.
#
import os
import sys
import logging as log

from astropy.io import fits

from config.settings import OUTPUT_DIR
import imdtk.core.fits_utils as fits_utils
# from imdtk.core.i_tool import ITool         # LATER: IMPLEMENT and uncomment


class HeadersTool ():
    """ Class for extracting header information from FITS files. """

    def __init__(self, args):
        """ Constructor for the class extracting header information from FITS files. """

        # Display name of this tool
        self.TOOL_NAME = args.get('TOOL_NAME') or 'headers'

        # Configuration parameters given to this class.
        self.args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = args.get('debug', False)

        # An output file created within the output directory.
        self._output_file = None

        # Output format for the information when output.
        self._output_format = args.get('output_format') or 'json'


    #
    # Concrete methods implementing ITool abstract methods
    #

    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for this instance. """
        if (self._DEBUG):
            print("({}).cleanup)".format(self.TOOL_NAME))
        if (self._output_file is not None):
            self._output_file.close()
            self._output_file = None


    def process_and_output (self):
        """ Perform the main work of the tool and output the results in the selected format. """
        results = self.process()
        if (results):
            self.output_results(results)


    def process (self):
        """ Perform the main work of the tool and return the results as a Python structure. """

        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args))

        # process the given, validated FITS file
        fits_file = self.args.get('fits_file')
        if (self._VERBOSE):
            print("({}.process): Processing FITS file '{}'".format(self.TOOL_NAME, fits_file))

        ignore_list = self.args.get('ignore_list', [])
        which_hdu = self.args.get('which_hdu', 0)

        try:
            with fits.open(fits_file) as hdus_list:
                if (ignore_list):
                    hdrs = fits_utils.get_header_fields(hdus_list, which_hdu, ignore_list)
                else:
                    hdrs = fits_utils.get_header_fields(hdus_list, which_hdu)

                if (hdrs is None):
                    errMsg = "({}.process): Unable to read metadata from FITS file '{}'.".format(self.TOOL_NAME, fits_file)
                    log.error(errMsg)
                    raise RuntimeError(errMsg)

                return hdrs                 # return the results of processing

        except Exception as ex:
            errMsg = "({}.process): Exception while reading metadata from FITS file '{}': {}.".format(self.TOOL_NAME, fits_file, ex)
            log.error(errMsg)
            raise RuntimeError(errMsg)


    def output_results (self, results):
        """ Output the given results in the selected format. """

        # TODO: IMPLEMENT WRITING OUTPUT AS JSON
        if (self._VERBOSE):
            print("({}): HEADERS: {}".format(self.TOOL_NAME, results)) # REMOVE LATER

        # TODO: maybe use LATER?
        # if (self._output_format != 'db'):   # if writing to a file
        #     out_file_path = self.gen_output_file_path(OUTPUT_DIR)
        #     self._output_file = open(out_file_path, 'w')


    #
    # Non-interface Methods
    #

    def to_JSON (self, fields_info):
        """ Return the given field information formatted as a JSON string. """
        return '[]'                         # JSON NOT YET IMPLEMENTED
