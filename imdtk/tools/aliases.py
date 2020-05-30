#
# Class for adding aliases (fields) for the header fields in the FITS metadata structure.
#   Written by: Tom Hicks. 5/29/2020.
#   Last Modified: Initial creation.
#
import os
import sys
import configparser
import datetime
import json
import pickle
import logging as log

import imdtk.core.file_utils as file_utils
import imdtk.core.fits_utils as fits_utils
from config.settings import CONFIG_DIR
from imdtk.tools.i_tool import IImdTool


class AliasesTool (IImdTool):
    """ Class for adding aliases to the the FITS metadata structure. """

    # Default resource file for header keyword aliases.
    DEFAULT_ALIASES_FILEPATH = "{}/jwst-aliases.ini".format(CONFIG_DIR)


    def __init__(self, args):
        """ Constructor for the class adding aliases to the FITS metadata structure. """

        # Display name of this tool
        self.TOOL_NAME = args.get('TOOL_NAME') or 'aliases'

        # Configuration parameters given to this class.
        self.args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = args.get('debug', False)

        # Path to a readable input metadata file.
        self._input_file = args.get('input_file')

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
        input_file = self.args.get('input_file')
        if (self._VERBOSE):
            print("({}): Processing metadata file '{}'".format(self.TOOL_NAME, input_file))

        try:
            metadata = json.load(input_file)

            # load the FITS field name aliases from a given file path or a default resource path
            alias_file = self._args.get('alias_file') or self.DEFAULT_ALIASES_FILEPATH
            aliases = self.load_aliases(alias_file)

            self.copy_aliased_fields(aliases, metadata)
            return metadata                 # return the results of processing

        except Exception as ex:
            errMsg = "({}.process): Exception while reading metadata from file '{}': {}.".format(self.TOOL_NAME, input_file, ex)
            log.error(errMsg)
            raise RuntimeError(errMsg)


    def output_results (self, headers):
        """ Output the given headers in the selected format. """
        out_fmt = self._output_format

        sink = self._output_sink
        if (sink == 'file'):                # if output file specified
            if (out_fmt == 'pickle'):
                self._output_file = open(self.gen_output_file_path(), 'wb')
            else:
                self._output_file = open(self.gen_output_file_path(), 'w')
        else:                               # else default to standard output
            self._output_file = sys.stdout

        if (out_fmt == 'json'):
            self.output_JSON(headers)
        elif (out_fmt == 'pickle'):
            self.output_pickle(headers)
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

    def copy_aliased_headers (self, aliases, metadata):
        copied = dict()
        headers = metadata.get('headers')
        if (headers is not None):
            copied = { key: val for key, val in headers.items() if (key in aliases) }
        metadata['aliases'] = copied


    def into_context (self, headers):
        """ Embed the headers into a larger structure; include input_file info, if possible. """
        results = dict()
        self.add_file_info(results)
        results['headers'] = headers
        return results


    def load_aliases (self, alias_file):
        """ Load field name aliases from the given alias filepath. """
        if (self._VERBOSE):
            print("({}.load_aliases): Loading from aliases file '{}'".format(TOOL_NAME, alias_file))

        config = configparser.ConfigParser(strict=False, empty_lines_in_values=False)
        config.optionxform = lambda option: option
        config.read(alias_file)
        aliases = config['aliases']

        if (self._VERBOSE):
            print("({}.load_aliases): Read {} field name aliases.".format(TOOL_NAME, len(aliases)))
        return dict(aliases)


    def output_JSON (self, headers):
        # embed the headers into a larger structure, including input_file info
        results = self.into_context(headers)
        json.dump(results, self._output_file, indent=2)
        self._output_file.write('\n')


    def output_pickle (self, headers):
        # embed the headers into a larger structure, including input_file info
        results = self.into_context(headers)
        pickle.dump(results, self._output_file)
