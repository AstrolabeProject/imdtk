#
# Class to add aliases (fields) for the header fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 5/29/2020.
#   Last Modified: Remove unused imports.
#
import os
import sys
import configparser
import logging as log

from config.settings import DEFAULT_ALIASES_FILEPATH
import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import IImdTask


class AliasesTask (IImdTask):
    """ Class which adds aliases for the header fields of a metadata structure. """

    def __init__(self, args):
        """
        Constructor for class which adds aliases for the header fields of a metadata structure.
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

        # load the FITS field name aliases from a given file path or a default resource path
        alias_file = self.args.get('alias_file') or DEFAULT_ALIASES_FILEPATH
        aliases = self.load_aliases(alias_file)

        self.copy_aliased_headers(aliases, metadata) # add aliased fields

        return metadata                     # return the results of processing


    #
    # Non-interface and/or task-specific Methods
    #

    def copy_aliased_headers (self, aliases, metadata):
        """
        Copy each header card whose key is in aliases, replacing the header key with the alias.
        """
        copied = dict()
        headers = md_utils.get_headers(metadata)
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
