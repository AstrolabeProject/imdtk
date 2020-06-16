#
# Class to add information about desired fields to the FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/9/2020.
#   Last Modified: Move default file paths to config/settings.
#
import os, sys
import configparser
import logging as log
import toml

from config.settings import DEFAULT_FIELDS_FILEPATH
from imdtk.tasks.i_task import IImdTask, STDIN_NAME, STDOUT_NAME
import imdtk.tasks.metadata_utils as md_utils


class FieldsInfoTask (IImdTask):
    """ Class which adds field information to a metadata structure. """

    def __init__(self, args):
        """
        Constructor for class which adds field information to a metadata structure.
        """
        super().__init__(args)


    #
    # Concrete methods implementing ITask abstract methods
    #

    def process (self, metadata):
        """
        Perform the main work of the task on the given metadata and return the results
        as a Python data structure.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # load the field information from a given file path or a default resource path
        fields_file = self.args.get('fields_file') or DEFAULT_FIELDS_FILEPATH
        if (self._VERBOSE):
            print("({}): Loading from fields info file '{}'".format(self.TOOL_NAME, fields_file), file=sys.stderr)

        fields_info = self.load_fields_info(fields_file)

        if (self._VERBOSE):
            print("({}): Read {} fields.".format(self.TOOL_NAME, len(fields_info)), file=sys.stderr)

        metadata['fields_info'] = fields_info # add field information to metadata

        defaults = self.extract_defaults(fields_info)
        metadata['defaults'] = defaults     # add defaults dictionary to metadata

        return metadata                 # return the results of processing


    def output_results (self, metadata):
        """ Output the given metadata in the configured output format. """
        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')
        out_fmt = self.args.get('output_format') or 'json'

        if (out_fmt == 'json'):
            if (genfile):                   # if generating the output filename/path
                file_info = md_utils.get_file_info(metadata)
                fname = file_info.get('file_name') if file_info else "NO_FILENAME"
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
    # Non-interface and/or task-specific Methods
    #

    def load_fields_info (self, fields_file):
        """
        Load the fields info dictionary from the given filepath and return it.
        The fields info file is assumed to define a single dictionary in TOML format.
        """
        return toml.load(fields_file)       # load fields info file as a dictionary


    def extract_defaults (self, fields_info):
        """
        Given a dictionary of fields information, extract the fields with default values and
        return a dictionary of field defaults of the form: "field_name => default_value".
        """
        return { k:v.get('default') for (k, v) in fields_info.items() if 'default' in v }
