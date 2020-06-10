#
# Class to add defaults (fields) for the fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/9/2020.
#   Last Modified: Refactor reading input JSON to parent class.
#
import os
import sys
import configparser
# import datetime     # REMOVE: unused?
import json
import logging as log

from config.settings import CONFIG_DIR
from imdtk.tools.i_tool import IImdTool, STDIN_NAME, STDOUT_NAME
import imdtk.core.fields_file_reader as fields_file_reader


# Default resource file for default field values.
DEFAULT_FIELDS_FILEPATH = "{}/jwst-fields.txt".format(CONFIG_DIR)


class DefaultsTool (IImdTool):
    """ Class which adds defaults for the fields of a metadata structure. """

    def __init__(self, args):
        """
        Constructor for class which adds defaults for the fields of a metadata structure.
        """

        # Display name of this tool
        self.TOOL_NAME = args.get('TOOL_NAME') or 'defaults'

        # Configuration parameters given to this class.
        self.args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = args.get('debug', False)


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

        # load the field information from a given file path or a default resource path
        fields_file = self.args.get('fields_file') or DEFAULT_FIELDS_FILEPATH
        defaults = self.load_defaults(fields_file)

        # process the given, already validated input file
        input_file = self.args.get('input_file')
        if (self._VERBOSE):
            if (input_file is None):
                print("({}): Processing metadata from {}".format(self.TOOL_NAME, STDIN_NAME))
            else:
                print("({}): Processing metadata file '{}'".format(self.TOOL_NAME, input_file))

        # read metadata from the input file in the specified input format
        input_format = self.args.get('input_format') or DEFAULT_INPUT_FORMAT
        metadata = self.input_JSON(input_file, input_format, self.TOOL_NAME)

        metadata['defaults'] = defaults # add defaults dictionary to metadata

        return metadata                 # return the results of processing


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
            print("({}): Results output to '{}'".format(self.TOOL_NAME, out_dest))



    #
    # Non-interface (tool-specific) Methods
    #

    def load_defaults (self, fields_file):
        """ Load field defaults from the given fields information filepath. """
        if (self._VERBOSE):
            print("({}.load_defaults): Loading from fields info file '{}'".format(self.TOOL_NAME, fields_file))

        defaults = fields_file_reader.load(fields_file)

        if (self._VERBOSE):
            print("({}.load_defaults): Read {} field defaults.".format(self.TOOL_NAME, len(defaults)))

        return defaults
