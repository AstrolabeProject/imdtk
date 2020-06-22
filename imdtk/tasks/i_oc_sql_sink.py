#
# Class defining interface methods to store incoming data to an SQL database.
#   Written by: Tom Hicks. 6/21/2020.
#   Last Modified: Initial creation.
#
import os
import sys
import configparser

from imdtk.tasks.i_task import IImdTask


class IObsCoreSQLSink (IImdTask):
    """
    Class defining interface methods to store incoming data to an SQL database.
    """

    # Value which identifies records which are public: 0 means is_public = false
    IS_PUBLIC_VALUE = 0

    # String which defines a comment line in the SQL output.
    SQL_COMMENT = '--'


    def __init__(self, args):
        """
        Constructor for class defining interface methods to store incoming data to an SQL database.
        """
        super().__init__(args)


    #
    # Non-interface and/or sink-specific Methods
    #

    def load_db_configuration (self, dbconfig_file):
        """
        Load the database configuration from the given filepath. Returns a dictionary
        of database configuration parameters.
        """
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(),
                                           strict=False, empty_lines_in_values=False)
        # config.optionxform = lambda option: option          # IS NEEDED? REMOVE LATER?
        config.read(dbconfig_file)
        dbconfig = config['db_properties']
        return dict(dbconfig)
