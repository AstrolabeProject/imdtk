#
# Class to add aliases (fields) for the header fields in a FITS-derived image metadata structure.
#   Written by: Tom Hicks. 5/29/2020.
#   Last Modified: Update for separate alias utilities and renamed alias file path.
#
import sys

from config.settings import DEFAULT_IMD_ALIASES_FILEPATH
import imdtk.core.alias_utils as alias_utils
import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import IImdTask


class AliasesTask (IImdTask):
    """
    Class which adds aliases for the header fields of an image metadata structure.
    """

    def __init__(self, args):
        """
        Constructor for class which adds aliases for the header fields of an
        image metadata structure.
        """
        super().__init__(args)


    #
    # Methods overriding IImdTask interface methods
    #

    def process (self, metadata):
        """
        Perform the main work of the task on the given metadata and return the results
        as a Python data structure.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # load the FITS field name aliases from a given file path or a default resource path
        alias_file = self.args.get('alias_file') or DEFAULT_IMD_ALIASES_FILEPATH
        aliases = alias_utils.load_aliases(alias_file, self._DEBUG, tool_name=self.TOOL_NAME)

        headers = md_utils.get_headers(metadata)
        metadata['aliased'] = alias_utils.copy_aliased_headers(aliases, headers)

        return metadata                     # return the results of processing
