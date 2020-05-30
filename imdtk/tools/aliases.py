#
# Class to add aliases (fields) for the header fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 5/29/2020.
#   Last Modified: Implement first working version, cleanup.
#
import os
import sys
import configparser
import datetime
import json
import pickle
import logging as log

from config.settings import CONFIG_DIR
from imdtk.tools.i_tool import IImdTool


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
                print("({}): Processing metadata from standard input".format(self.TOOL_NAME))
            else:
                print("({}): Processing metadata file '{}'".format(self.TOOL_NAME, self._input_file.name))

        try:
            metadata = json.load(self._input_file)
            self.copy_aliased_headers(aliases, metadata)
            return metadata                 # return the results of processing

        except Exception as ex:
            errMsg = "({}.process): Exception while reading metadata from file '{}': {}.".format(self.TOOL_NAME, self._input_file, ex)
            log.error(errMsg)
            raise RuntimeError(errMsg)


    def output_results (self, metadata):
        """ Output the given metadata in the selected format. """
        out_fmt = self._output_format

        fname = metadata.get('file_info').get('file_name')

        sink = self._output_sink
        if (sink == 'file'):                # if output file specified
            if (out_fmt == 'pickle'):
                self._output_file = open(
                    self.gen_output_file_path(fname, self._output_format, self.TOOL_NAME), 'wb')
            else:
                self._output_file = open(
                    self.gen_output_file_path(fname, self._output_format, self.TOOL_NAME), 'w')
        else:                               # else default to standard output
            self._output_file = sys.stdout

        if (out_fmt == 'json'):
            self.output_JSON(metadata)
        elif (out_fmt == 'pickle'):
            self.output_pickle(metadata)
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


    def output_JSON (self, metadata):
        json.dump(metadata, self._output_file, indent=2)
        self._output_file.write('\n')


    def output_pickle (self, metadata):
        pickle.dump(metadata, self._output_file)
