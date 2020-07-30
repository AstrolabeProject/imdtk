#
# Module defining base test methods for testing SQL database code.
#   Written by: Tom Hicks. 7/29/2020.
#   Last Modified: Initial creation from main SQL interface.
#
import configparser
import sys

from tests import TEST_DBCONFIG_FILEPATH


def load_test_dbconfig (dbconfig_file=TEST_DBCONFIG_FILEPATH, debug=True, tool_name='SQL_TEST_SETUP'):
    """
    Load the database configuration from the given filepath. Returns a dictionary
    of database configuration parameters.
    """
    if (debug):
        print("({}): Reading Test DB configuration file '{}'".format(tool_name, dbconfig_file), file=sys.stderr)

    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(), strict=False, empty_lines_in_values=False)
    config.read(dbconfig_file)
    dbconfig = dict(config['db_properties'])

    if (debug):
        print("({}): Read {} Test DB configuration properties.".format(tool_name, len(dbconfig)), file=sys.stderr)

    return dbconfig
