#
# Class to add aliases (fields) for the header fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 5/29/2020.
#   Last Modified: Replace pickling with CSV output stubs.
#
import os
import sys
import configparser
import datetime
import json
import logging as log

from config.settings import CONFIG_DIR
from imdtk.tools.i_tool import IImdTool, STDIN_NAME, STDOUT_NAME


# Default resource file for header keyword aliases.
DEFAULT_ALIASES_FILEPATH = "{}/jwst-aliases.ini".format(CONFIG_DIR)


class AliasesTool (IImdTool):
    """ Class which adds aliases for the header fields of a metadata structure. """

    def __init__(self, args):
        """ Constructor of the class which adds aliases for the header fields of a metadata structure. """

        # Display name of this tool
        self.TOOL_NAME = args.get('TOOL_NAME') or 'aliases'

        # Configuration parameters given to this class.
        self.args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = args.get('debug', False)

        # Path to a readable input metadata file. Argument is optional so could be None.
        self._input_file = args.get('input_file')

        # Input format for the metadata to be processed.
        self._input_format = args.get('input_format') or 'json'

        # Output format for the information when output.
        self._output_format = args.get('output_format') or 'json'

        # Where to send the processing results from this tool.
        self._output_sink = args.get('output_sink')

        # An output file to be created within the output directory.
        self._output_file = None


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

        # load the FITS field name aliases from a given file path or a default resource path
        alias_file = self.args.get('alias_file') or DEFAULT_ALIASES_FILEPATH
        aliases = self.load_aliases(alias_file)

        # process the given, validated input file
        if (self._input_file is None):
            self._input_file = sys.stdin
        else:
            self._input_file = open(self._input_file, 'r')

        if (self._VERBOSE):
            if (self._input_file == sys.stdin):
                print("({}): Processing metadata from {}".format(self.TOOL_NAME, STDIN_NAME))
            else:
                print("({}): Processing metadata file '{}'".format(self.TOOL_NAME, self._input_file.name))

        try:
            in_fmt = self._input_format
            if (in_fmt == 'json'):
                metadata = json.load(self._input_file)
            else:
                errMsg = "({}.process): Invalid input format '{}'.".format(self.TOOL_NAME, in_fmt)
                log.error(errMsg)
                raise ValueError(errMsg)

            self.copy_aliased_headers(aliases, metadata)
            return metadata                 # return the results of processing

        except Exception as ex:
            errMsg = "({}.process): Exception while reading metadata from file '{}': {}.".format(self.TOOL_NAME, self._input_file, ex)
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
                self.output_csv(csv, sink)

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

    def copy_aliased_headers (self, aliases, metadata):
        """
        Copy each header card whose key is in aliases, replacing the header key with the alias.
        """
        copied = dict()
        headers = metadata.get('headers')
        if (headers is not None):
            for hdr_key, hdr_val in headers.items():
                a_key = aliases.get(hdr_key)
                if (a_key is not None):
                    copied[a_key] = hdr_val
        metadata['aliased'] = copied        # add copied aliases dictionary to metadata


    def load_aliases (self, alias_file):
        """ Load field name aliases from the given alias filepath. """
        if (self._VERBOSE):
            print("({}.load_aliases): Loading from aliases file '{}'".format(self.TOOL_NAME, alias_file))

        config = configparser.ConfigParser(strict=False, empty_lines_in_values=False)
        config.optionxform = lambda option: option
        config.read(alias_file)
        aliases = config['aliases']

        if (self._VERBOSE):
            print("({}.load_aliases): Read {} field name aliases.".format(self.TOOL_NAME, len(aliases)))
        return dict(aliases)


    def toCSV (self, metadata):
        """ Convert the given metadata to CSV and return a CSV string. """
        return ''                           # TODO: IMPLEMENT LATER
