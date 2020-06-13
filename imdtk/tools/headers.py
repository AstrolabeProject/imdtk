#
# Class for extracting header information from FITS files.
#   Written by: Tom Hicks. 5/23/2020.
#   Last Modified: Rename this as task.
#
import os, sys
import json
import logging as log

from astropy.io import fits

import imdtk.core.fits_utils as fits_utils
from imdtk.tools.i_tool import IImdTask, STDOUT_NAME


class HeadersSourceTask (IImdTask):
    """ Class for extracting header information from FITS files. """

    def __init__(self, args):
        """ Constructor for the class extracting header information from FITS files. """

        # Display name of this task
        self.TOOL_NAME = args.get('TOOL_NAME') or 'headers'

        # Configuration parameters given to this class.
        self.args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = args.get('debug', False)

        # Path to a readable FITS image file from which to extract metadata.
        self._fits_file = args.get('fits_file')


    #
    # Concrete methods implementing ITask abstract methods
    #

    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for this instance. """
        if (self._DEBUG):
            print("({}.cleanup)".format(self.TOOL_NAME), file=sys.stderr)


    def process_and_output (self):
        """ Perform the main work of the task and output the results in the selected format. """
        metadata = self.process()
        if (metadata):
            self.output_results(metadata)


    def process (self):
        """
        Perform the main work of the task and return the results as a Python structure.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # process the given, already validated FITS file
        fits_file = self.args.get('fits_file')
        if (self._VERBOSE):
            print("({}): Processing FITS file '{}'".format(self.TOOL_NAME, fits_file), file=sys.stderr)

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

            metadata = self.make_context()  # create larger metadata structure
            metadata['headers'] = hdrs      # add the headers to the metadata
            return metadata                 # return the results of processing

        except Exception as ex:
            errMsg = "({}.process): Exception while reading metadata from FITS file '{}': {}.".format(self.TOOL_NAME, fits_file, ex)
            log.error(errMsg)
            raise RuntimeError(errMsg)


    def output_results (self, metadata):
        """ Output the given metadata in the selected format. """
        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')
        out_fmt = self.args.get('output_format') or 'json'

        if (out_fmt == 'json'):
            if (genfile):                   # if generating the output filename/path
                fname = metadata.get('file_info').get('file_name')
                outfile = self.gen_output_file_path(fname, out_fmt, self.TOOL_NAME)
                self.output_JSON(metadata, outfile)
            elif (outfile is not None):     # else if using the given filepath
                self.output_JSON(metadata, outfile)
            else:                           # else using standard output
                self.output_JSON(metadata)

        else:
            errMsg = "({}.process): Invalid output format '{}'.".format(self.TOOL_NAME, out_fmt)
            log.error(errMsg)
            raise ValueError(errMsg)

        if (self._VERBOSE):
            out_dest = outfile if (outfile) else STDOUT_NAME
            print("({}): Results output to '{}'".format(self.TOOL_NAME, out_dest), file=sys.stderr)


    #
    # Non-interface and/or Task-specific Methods
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
