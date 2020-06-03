#
# Class for extracting header information from FITS files.
#   Written by: Tom Hicks. 5/23/2020.
#   Last Modified: Remove unused output file instance var.
#
import os
import sys
import json
import logging as log

from astropy.io import fits

import imdtk.core.fits_utils as fits_utils
from imdtk.tools.i_tool import IImdTool, STDOUT_NAME


class HeadersSourceTool (IImdTool):
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

        # Path to a readable FITS image file from which to extract metadata.
        self._fits_file = args.get('fits_file')

        # Output format for the information when output.
        self._output_format = args.get('output_format') or 'json'

        # Where to send the processing results from this tool.
        self._output_sink = args.get('output_sink')


    #
    # Concrete methods implementing ITool abstract methods
    #

    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for this instance. """
        if (self._DEBUG):
            print("({}.cleanup)".format(self.TOOL_NAME))


    def process_and_output (self):
        """ Perform the main work of the tool and output the results in the selected format. """
        metadata = self.process()
        if (metadata):
            self.output_results(metadata)


    def process (self):
        """
        Perform the main work of the tool and return the results as a Python structure.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args))

        # process the given, validated FITS file
        fits_file = self.args.get('fits_file')
        if (self._VERBOSE):
            print("({}): Processing FITS file '{}'".format(self.TOOL_NAME, fits_file))

        ignore_list = self.args.get('ignore_list')
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

            metadata = self.into_context(hdrs)
            return metadata                 # return the results of processing

        except Exception as ex:
            errMsg = "({}.process): Exception while reading metadata from FITS file '{}': {}.".format(self.TOOL_NAME, fits_file, ex)
            log.error(errMsg)
            raise RuntimeError(errMsg)


    def output_results (self, metadata):
        """ Output the given metadata in the selected format. """
        file_path = None
        sink = self._output_sink

        out_fmt = self._output_format
        if (out_fmt == 'json'):
            if (sink == 'file'):
                fname = metadata.get('file_info').get('file_name')
                file_path = self.gen_output_file_path(fname, self._output_format, self.TOOL_NAME)
                self.output_JSON(metadata, file_path)
            else:
                self.output_JSON(metadata)

        elif (out_fmt == 'csv'):
            csv = self.toCSV(metadata)      # convert metadata to CSV
            if (sink == 'file'):
                fname = metadata.get('file_info').get('file_name')
                file_path = self.gen_output_file_path(fname, self._output_format, self.TOOL_NAME)
                self.output_csv(csv, file_path)
            else:
                self.output_csv(csv)

        else:
            errMsg = "({}.process): Invalid output format '{}'.".format(self.TOOL_NAME, out_fmt)
            log.error(errMsg)
            raise ValueError(errMsg)

        if (self._VERBOSE):
            out_dest = sink                 # default to current sink value
            if (sink == 'file'):            # reset value if necessary
                out_dest = file_path if (file_path) else STDOUT_NAME
            print("({}): Results output to '{}'".format(self.TOOL_NAME, out_dest))



    #
    # Non-interface (tool-specific) Methods
    #

    def add_file_info (self, results):
        """ Add information about the input file to the given results map. """
        file_info = dict()
        fits_file = self.args.get('fits_file')
        file_info['file_name'] = os.path.basename(fits_file)
        file_info['file_path'] = os.path.abspath(fits_file)
        file_info['file_size'] = os.path.getsize(fits_file)
        results['file_info'] = file_info


    def into_context (self, headers):
        """ Embed the headers into a larger structure; include fits_file info, if possible. """
        results = dict()
        self.add_file_info(results)
        results['headers'] = headers
        return results


    def toCSV (self, metadata):
        """ Convert the given metadata to CSV and return a CSV string. """
        return ''                           # TODO: IMPLEMENT LATER
