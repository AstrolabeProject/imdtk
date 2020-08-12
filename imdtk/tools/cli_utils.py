#
# Class defining utility methods for tool components CLI.
#   Written by: Tom Hicks. 6/1/2020.
#   Last Modified: Remove version argument: read from file.
#
import argparse
import sys

from config.settings import DEFAULT_IMD_ALIASES_FILEPATH, DEFAULT_DBCONFIG_FILEPATH
from config.settings import DEFAULT_FIELDS_FILEPATH, DEFAULT_METADATA_TABLE_NAME
from imdtk.version import VERSION
from imdtk.core.file_utils import good_dir_path, good_file_path, validate_file_path
from imdtk.core.fits_utils import FITS_EXTENTS


# required arguments:
FITS_FILE_EXIT_CODE = 20
INPUT_DIR_EXIT_CODE = 21
CATALOG_TABLE_EXIT_CODE = 22

# optional arguments:
ALIAS_FILE_EXIT_CODE = 30
DBCONFIG_FILE_EXIT_CODE = 31
FIELDS_FILE_EXIT_CODE = 32
INPUT_FILE_EXIT_CODE = 33


def add_aliases_arguments (parser, tool_name, default_msg=DEFAULT_IMD_ALIASES_FILEPATH):
    """ Add the argument(s) related to parsing information from aliases files
        to the given argparse parser object. """
    parser.add_argument(
        '-a', '--aliases', dest='alias_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help="Path to file of aliases for metadata header fields [default: {}]".format(default_msg)
    )


def add_catalog_table_arguments (parser, tool_name, default_msg='no default'):
    """ Add the argument(s) related to naming a database table for a catalog
        to the given argparse parser object. """
    parser.add_argument(
        '-ct', '--catalog-table', dest='catalog_table', required=True, metavar='schema.table',
        help="Catalog table name in the database [default: {}]".format(default_msg)
    )


def add_collection_arguments (parser, tool_name, default_msg='no default'):
    """ Add the argument(s) related to collection specification
        to the given argparse parser object. """
    parser.add_argument(
        '-c', '--collection', dest='collection', metavar='collection-name',
        default=argparse.SUPPRESS,
        help="Collection name for ingested images [default: {}]".format(default_msg)
    )


def add_database_arguments (parser, tool_name,
                            default_msg=DEFAULT_DBCONFIG_FILEPATH,
                            table_msg=DEFAULT_METADATA_TABLE_NAME):
    """ Add the argument(s) related to parsing information from a database configuration file
        to the given argparse parser object. """
    parser.add_argument(
        '-db', '--db-config', dest='dbconfig_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help="Path to database configuration file [default: {}]".format(default_msg)
    )

    parser.add_argument(
        '-tn', '--table-name', dest='table_name', metavar='schema.table',
        default=argparse.SUPPRESS,
        help="Table name for data to be stored in the database [default: {}]".format(table_msg)
    )

    parser.add_argument(
        '-sql', '--sql-only', dest='sql_only', action='store_true',
        default=False,
        help='If True, output SQL only and do NOT store the data in the database [default: False].'
    )


def add_fields_info_arguments (parser, tool_name, default_msg=DEFAULT_FIELDS_FILEPATH):
    """ Add the argument(s) related to parsing information from fields information files
        to the given argparse parser object. """
    parser.add_argument(
        '-fi', '--fields-info', dest='fields_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help="Path to fields information file [default: {}]".format(default_msg)
    )


def add_fits_file_arguments (parser, tool_name):
    """ Add the argument(s) related to parsing information from FITS files
        to the given argparse parser object. """
    parser.add_argument(
        '-ff', '--fits-file', dest='fits_file', required=True, metavar='filepath',
        help='Path to a readable FITS image file from which to extract metadata [required]'
    )
    add_hdu_arguments(parser, tool_name)  # now add HDU argument


def add_hdu_arguments (parser, tool_name):
    """ Add the argument(s) related to parsing information from HDUs of FITS files
        to the given argparse parser object. """
    parser.add_argument(
        '-hdu', '--hdu', dest='which_hdu', metavar='HDU_index',
        default=0, type=int,
        help='Index of HDU containing the metadata [default: 0 (the first)]'
    )


def add_input_arguments (parser, tool_name):
    """ Add common input arguments to the given argparse parser object. """
    # parser.add_argument(
    #     '-ifmt', '--input-format', dest='input_format',
    #     default='json',
    #     choices=['json', 'text'],
    #     help='Format of input data file: "json" or "text" [default: "json"]'
    # )

    parser.add_argument(
        '-if', '--input-file', dest='input_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help='Path to a readable input data file [default: (standard input)]'
    )


def add_input_dir_arguments (parser, tool_name):
    """ Add the argument(s) related to parsing information from a directory of input files
        to the given argparse parser object. """
    parser.add_argument(
        '-idir', '--input-dir', dest='input_dir', required=True, metavar='dirpath',
        help='Path to a readable directory of input files to process [required]'
    )


def add_output_arguments (parser, tool_name):
    """ Add common output arguments to the given argparse parser object. """
    parser.add_argument(
        '-g', '--generate', dest='gen_file_path', action='store_true',
        default=False,
        help='Automatically generate the output filename and path. [default: False].'
    )

    parser.add_argument(
        '-of', '--output-file', dest='output_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help='File path of file to hold the processing results [default: (standard output)]'
    )

    # parser.add_argument(
    #     '-ofmt', '--output-format', dest='output_format',
    #     default='json',
    #     choices=['json', 'other'],
    #     help='Output format for results: "json" or "other" [default: "json"]'
    # )


def add_report_arguments (parser, tool_name):
    # parser.add_argument(
    #     '-rf', '--report-file', dest='report_file', metavar='filepath',
    #     default=argparse.SUPPRESS,
    #     help='File path of file to hold the output report [default: (standard error)]'
    # )

    parser.add_argument(
        '-rfmt', '--report-format', dest='report_format',
        default='text',
        choices=['json', 'text'],
        help='Output format for reports: "json" or "text" [default: "text"]'
    )


def add_shared_arguments (parser, tool_name):
    """ Add the arguments shared by all tools to the given argparse parser object. """
    parser.add_argument(
        '--version', action='version', version="{} version {}".format(tool_name, VERSION),
        help='Show version information and exit.'
    )

    parser.add_argument(
        '-d', '--debug', dest='debug', action='store_true',
        default=False,
        help='Print debugging output during processing [default: False (non-debug mode)]'
    )

    parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true',
        default=False,
        help='Print informational messages during processing [default: False (non-verbose mode)].'
    )


def check_catalog_table (catalog_table_name, tool_name, exit_code=CATALOG_TABLE_EXIT_CODE):
    """
    Check that the required catalog table name is provided If not, then exit
    the entire program here with the specified (or default) system exit code.
    """
    if (not catalog_table_name):
        errMsg = "({}): A catalog table name must be specified. Exiting...".format(tool_name)
        print(errMsg, file=sys.stderr)
        sys.exit(exit_code)


def check_alias_file (alias_file, tool_name, exit_code=ALIAS_FILE_EXIT_CODE):
    """
    If a path to an aliases file is given, check that it is a good path. If not, then exit
    the entire program here with the specified (or default) system exit code.
    """
    if (alias_file):                        # if aliases file given, check it
        if (not good_file_path(alias_file)):
            errMsg = "({}): A readable aliases file must be specified. Exiting...".format(tool_name)
            print(errMsg, file=sys.stderr)
            sys.exit(exit_code)


def check_dbconfig_file (dbconfig_file, tool_name, exit_code=DBCONFIG_FILE_EXIT_CODE):
    """
    If a path to a DB configuration file is given, check that it is a good path. If not,
    then exit the entire program here with the specified (or default) system exit code.
    """
    if (dbconfig_file):                     # if DB configuration file given, check it
        if (not good_file_path(dbconfig_file)):
            errMsg = "({}): A readable database configuration file must be specified. Exiting...".format(tool_name)
            print(errMsg, file=sys.stderr)
            sys.exit(exit_code)


def check_fields_file (fields_file, tool_name, exit_code=FIELDS_FILE_EXIT_CODE):
    """
    If a path to an aliases file is given, check that it is a good path. If not, then exit
    the entire program here with the specified (or default) system exit code.
    """
    if (fields_file):                       # if fields info file given, check it
        if (not good_file_path(fields_file)):
            errMsg = "({}): A readable fields information file must be specified. Exiting...".format(tool_name)
            print(errMsg, file=sys.stderr)
            sys.exit(exit_code)


def check_fits_file (fits_file, tool_name, exit_code=FITS_FILE_EXIT_CODE):
    """
    Check that the required FITS file path is a valid path. If not, then exit
    the entire program here with the specified (or default) system exit code.
    """
    if (not validate_file_path(fits_file, FITS_EXTENTS)):
        errMsg = "({}): A readable, valid FITS image file must be specified. Exiting...".format(tool_name)
        print(errMsg, file=sys.stderr)
        sys.exit(exit_code)


def check_input_dir (input_dir, tool_name, exit_code=INPUT_DIR_EXIT_CODE):
    """
    Check that the required input direct path is a valid path. If not, then exit
    the entire program here with the specified (or default) system exit code.
    """
    if (not good_dir_path(input_dir)):
        errMsg = "({}): A readable input directory must be specified. Exiting...".format(tool_name)
        print(errMsg, file=sys.stderr)
        sys.exit(exit_code)


def check_input_file (input_file, tool_name, exit_code=INPUT_FILE_EXIT_CODE):
    """
    If an input file path is given, check that it is a good path. If not, then exit
    the entire program here with the specified (or default) system exit code.
    """
    if (input_file):                        # if input file given, check it
        if (not good_file_path(input_file)):
            errMsg = "({}): A readable, valid input data file must be specified. Exiting...".format(tool_name)
            print(errMsg, file=sys.stderr)
            sys.exit(exit_code)
