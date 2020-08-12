#
# Class to add aliases (fields) for the column name fields in an Astropy-derived
# catalog information metadata structure.
#   Written by: Tom Hicks. 8/7/2020.
#   Last Modified: Update for renames.
#
import sys

from config.settings import DEFAULT_CAT_ALIASES_FILEPATH
import imdtk.core.alias_utils as alias_utils
import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import IImdTask


class CatalogAliasesTask (IImdTask):
    """
    Class which adds aliases for the column information fields of a catalog metadata structure.
    """

    def __init__(self, args):
        """
        Constructor for class which adds aliases for the column information fields of
        a catalog metadata structure.
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

        # load the column name information aliases from a given file path or a default resource path
        alias_file = self.args.get('alias_file') or DEFAULT_CAT_ALIASES_FILEPATH
        aliases = alias_utils.load_aliases(alias_file, self._DEBUG, tool_name=self.TOOL_NAME)

        col_names = md_utils.get_column_names(metadata)
        metadata['aliased'] = alias_utils.substitute_aliases(aliases, col_names)

        return metadata                     # return the results of processing
