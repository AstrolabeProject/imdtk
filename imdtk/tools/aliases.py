#
# Class to add aliases (fields) for the header fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 5/29/2020.
#   Last Modified: Update for rename to i_task.
#
import os, sys
import configparser
import datetime
import json
import logging as log

from config.settings import CONFIG_DIR
from imdtk.tools.i_task import IImdTask, STDIN_NAME, STDOUT_NAME


# Default resource file for header keyword aliases.
DEFAULT_ALIASES_FILEPATH = "{}/jwst-aliases.ini".format(CONFIG_DIR)


class AliasesTask (IImdTask):
    """ Class which adds aliases for the header fields of a metadata structure. """

    def __init__(self, args):
        """
        Constructor for class which adds aliases for the header fields of a metadata structure.
        """

        # Display name of this task
        self.TOOL_NAME = args.get('TOOL_NAME') or 'aliases'

        # Configuration parameters given to this class.
        self.args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = args.get('debug', False)


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

        # load the FITS field name aliases from a given file path or a default resource path
        alias_file = self.args.get('alias_file') or DEFAULT_ALIASES_FILEPATH
        aliases = self.load_aliases(alias_file)

        # process the given, already validated input file
        input_file = self.args.get('input_file')
        if (self._VERBOSE):
            if (input_file is None):
                print("({}): Processing metadata from {}".format(self.TOOL_NAME, STDIN_NAME), file=sys.stderr)
            else:
                print("({}): Processing metadata file '{}'".format(self.TOOL_NAME, input_file), file=sys.stderr)

        # read metadata from the input file in the specified input format
        input_format = self.args.get('input_format') or DEFAULT_INPUT_FORMAT
        metadata = self.input_JSON(input_file, input_format, self.TOOL_NAME)

        self.copy_aliased_headers(aliases, metadata) # add aliased fields

        return metadata                     # return the results of processing


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
            print("({}): Loading from aliases file '{}'".format(self.TOOL_NAME, alias_file), file=sys.stderr)

        config = configparser.ConfigParser(strict=False, empty_lines_in_values=False)
        config.optionxform = lambda option: option
        config.read(alias_file)
        aliases = config['aliases']

        if (self._VERBOSE):
            print("({}): Read {} field name aliases.".format(self.TOOL_NAME, len(aliases)), file=sys.stderr)
        return dict(aliases)
