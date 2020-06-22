#
# Class to add information about desired fields to the FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/9/2020.
#   Last Modified: Remove unused imports.
#
import os
import sys
import configparser
import logging as log
import toml

from config.settings import DEFAULT_FIELDS_FILEPATH
from imdtk.tasks.i_task import IImdTask


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

        return metadata                     # return the results of processing


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
