#
# Class to sink incoming ObsCore metadata to a PostgreSQL database.
#   Written by: Tom Hicks. 6/21/2020.
#   Last Modified: Initial creation.
#
import os, sys
import logging as log

from config.settings import DEFAULT_DBCONFIG_FILEPATH
from imdtk.tasks.i_oc_sql_sink import IObsCoreSQLSink


class JWST_ObsCorePostgreSQLSink (IObsCoreSQLSink):
    """ Class to sink incoming ObsCore metadata to a PostgreSQL database. """

    def __init__(self, args):
        """
        Constructor for class to sink incoming ObsCore metadata to a PostgreSQL database.
        """
        super().__init__(args)


    #
    # Methods overriding ITask interface methods
    #

    def output_results (self, metadata):
        """ Store the given metadata into the configured database. """
        if (self._DEBUG):
            print("({}.output_results): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # load the FITS field name aliases from a given file path or a default resource path
        dbconfig_file = self.args.get('dbconfig_file') or DEFAULT_DBCONFIG_FILEPATH
        dbconfig = self.load_db_config(dbconfig_file)

        print("DBCONFIG={}".format(dbconfig)) # REMOVE LATER


    #
    # Non-interface and/or task-specific Methods
    #

    def load_db_config (self, dbconfig_file):
        """ Load the database configuration from the given filepath. """
        if (self._VERBOSE):
            print("({}): Reading DB configuration file '{}'".format(self.TOOL_NAME, dbconfig_file), file=sys.stderr)

        dbconfig = self.load_db_configuration(dbconfig_file)

        if (self._VERBOSE):
            print("({}): Read {} DB configuration properties.".format(self.TOOL_NAME, len(dbconfig)), file=sys.stderr)

        return dbconfig
