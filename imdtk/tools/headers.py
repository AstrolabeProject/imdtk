#
# Class for extracting header information from FITS files.
#   Written by: Tom Hicks. 5/23/2020.
#   Last Modified: Use sink arg to write headers to JSON output. Add stubs for pickle output.
#                  Generate/use output filepath.
#
import os
import sys
import datetime
import json
import logging as log

from astropy.io import fits

from config.settings import OUTPUT_DIR
import imdtk.core.file_utils as file_utils
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

        # Path to a readable FITS image file from which to extract metadata.
        self._fits_file = args.get('fits_file')

        # An output file created within the output directory.
        self._output_file = None

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
        if (self._output_file is not None):
            self._output_file.close()
            self._output_file = None


    def process_and_output (self):
        """ Perform the main work of the tool and output the results in the selected format. """
        results = self.process()
        if (results):
            self.output_results(results)


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

            return hdrs                         # return the results of processing

        except Exception as ex:
            errMsg = "({}.process): Exception while reading metadata from FITS file '{}': {}.".format(self.TOOL_NAME, fits_file, ex)
            log.error(errMsg)
            raise RuntimeError(errMsg)


    def output_results (self, results):
        """ Output the given results in the selected format. """

        sink = self._output_sink
        if (sink == 'file'):                # if output file specified
            self._output_file = open(self.gen_output_file_path(), 'w')
        else:                               # else default to standard output
            self._output_file = sys.stdout

        out_fmt = self._output_format
        if (out_fmt == 'json'):
            self.output_JSON(results)
        elif (out_fmt == 'pickle'):
            self.output_pickle(results)
        else:
            errMsg = "({}.process): Invalid output format '{}'.".format(self.TOOL_NAME, out_fmt)
            log.error(errMsg)
            raise ValueError(errMsg)

        if (self._VERBOSE):
            out_dest = sink                 # default to current sink value
            if (sink == 'file'):            # reset value if necessary
                out_dest = self._output_file.name
            print("({}): Results output to '{}'".format(self.TOOL_NAME, out_dest))



    #
    # Non-interface Methods
    #

    def gen_output_file_path (self, out_dir=OUTPUT_DIR):
        """
        Return a unique output filepath, within the specified output directory,
        for the result file. Use the given file_name string and extension to create the name.
        """
        time_now = datetime.datetime.now()
        now_str = time_now.strftime("%Y%m%d_%H%M%S-%f")
        fname = file_utils.filename_core(self._fits_file)
        extension = self._output_format
        return "{0}/{1}_{2}.{3}".format(out_dir, fname, now_str, extension)


    def output_JSON (self, results):
        # TODO: merge results into a larger structure, including fits_file info

        json.dump(results, self._output_file, indent=2)
        self._output_file.write('\n')


    def output_pickle (self, results):
        # TODO: IMPLEMENT WRITING OUTPUT AS Pickle
        pass


    def to_JSON (self, fields_info):
        """ Return the given field information formatted as a JSON string. """
        return '[]'                         # JSON NOT YET IMPLEMENTED
