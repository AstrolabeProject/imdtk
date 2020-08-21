#
# Class defining utility methods for tool components CLI.
#   Written by: Tom Hicks. 6/1/2020.
#   Last Modified: Continue redo: separate table name argument, update doc strings.
#
import argparse
import sys

from config.settings import DEFAULT_IMD_ALIASES_FILEPATH, DEFAULT_DBCONFIG_FILEPATH
from config.settings import DEFAULT_FIELDS_FILEPATH, DEFAULT_METADATA_TABLE_NAME
from imdtk.version import VERSION
from imdtk.core.file_utils import good_dir_path, good_file_path, validate_file_path
from imdtk.core.fits_utils import FITS_EXTENTS, FITS_IGNORE_KEYS


# required arguments:
FITS_FILE_EXIT_CODE = 20
INPUT_DIR_EXIT_CODE = 21
CATALOG_TABLE_EXIT_CODE = 22

# optional arguments:
ALIAS_FILE_EXIT_CODE = 30
DBCONFIG_FILE_EXIT_CODE = 31
FIELDS_FILE_EXIT_CODE = 32
INPUT_FILE_EXIT_CODE = 33


def add_aliases_argument (parser, tool_name, default_msg=DEFAULT_IMD_ALIASES_FILEPATH):
    """ Add the argument, specifying the path to a file of data or metadata alias fields,
        to the given argparse parser object. """
    parser.add_argument(
        '-a', '--aliases', dest='alias_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help="Path to a file of aliases for data or metadata fields [default: {}]".format(default_msg)
    )


def add_catalog_hdu_argument (parser, tool_name):
    """ Add the argument, specifying which HDU of a FITS file contains the catalog data table,
        to the given argparse parser object. """
    parser.add_argument(
        '-chdu', '--catalog_hdu', dest='catalog_hdu', metavar='HDU_index',
        default=1, type=int,
        help='Index of the HDU containing the data table [default: 1 (the second)]'
    )


def add_catalog_table_argument (parser, tool_name, default_msg='no default'):
    """ Add the argument, naming a database catalog table,
        to the given argparse parser object. """
    parser.add_argument(
        '-ct', '--catalog-table', dest='catalog_table', required=True, metavar='table-name',
        help="Catalog table name in the database [default: {}]".format(default_msg)
    )


def add_collection_argument (parser, tool_name, default_msg='no default'):
    """ Add the argument, naming a specific data collection within the database,
        to the given argparse parser object. """
    parser.add_argument(
        '-c', '--collection', dest='collection', metavar='collection-name',
        default=argparse.SUPPRESS,
        help="Collection name for ingested images [default: {}]".format(default_msg)
    )


def add_database_arguments (parser, tool_name,
                            default_msg=DEFAULT_DBCONFIG_FILEPATH,
                            table_msg=DEFAULT_METADATA_TABLE_NAME):
    """ Add the arguments, related to configuration of the database,
        to the given argparse parser object. """
    parser.add_argument(
        '-db', '--db-config', dest='dbconfig_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help="Path to database configuration file [default: {}]".format(default_msg)
    )

    parser.add_argument(
        '-sql', '--sql-only', dest='sql_only', action='store_true',
        default=False,
        help='If True, output SQL only and do NOT store the data in the database [default: False].'
    )


def add_fields_info_argument (parser, tool_name, default_msg=DEFAULT_FIELDS_FILEPATH):
    """ Add the argument, specifying the path to file containing fields information,
        to the given argparse parser object. """
    parser.add_argument(
        '-fi', '--fields-info', dest='fields_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help="Path to fields information file [default: {}]".format(default_msg)
    )


def add_fits_file_argument (parser, tool_name):
    """ Add the argument, specifying a path to a file containing a FITS image or catalog,
        to the given argparse parser object. """
    parser.add_argument(
        '-ff', '--fits-file', dest='fits_file', required=True, metavar='filepath',
        help='Path to a readable FITS image file from which to extract data or metadata [required]'
    )


def add_hdu_argument (parser, tool_name):
    """ Add the argument, specifying which HDU of a FITS file contains the image metadata,
        to the given argparse parser object. """
    parser.add_argument(
        '-hdu', '--hdu', dest='which_hdu', metavar='HDU_index',
        default=0, type=int,
        help='Index of HDU containing the metadata [default: 0 (the first)]'
    )


def add_ignore_list_argument (parser, tool_name):
    """ Add the argument, specifying a single header keyword to ignore in the input,
        to the given argparse parser object. """
    parser.add_argument(
        '-ig', '--ignore', dest='ignore_list', action="append", metavar='header_key_to_ignore',
        default=argparse.SUPPRESS,
        help="Single header keyword to ignore (may repeat). [default: {} ]".format(FITS_IGNORE_KEYS)
    )


def add_input_dir_argument (parser, tool_name):
    """ Add the argument, specifying the path to a directory of input files,
        to the given argparse parser object. """
    parser.add_argument(
        '-idir', '--input-dir', dest='input_dir', required=True, metavar='dirpath',
        help='Path to a readable directory of input files to process [required]'
    )


def add_input_file_argument (parser, tool_name):
    """ Add the argument, specifying the path to a single input file,
        to the given argparse parser object. """
    parser.add_argument(
        '-if', '--input-file', dest='input_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help='Path to a readable input data file [default: (standard input)]'
    )


# def add_input_format_argument (parser, tool_name):
#     """ Add an input format specification argument to the given argparse parser object. """
#     parser.add_argument(
#         '-ifmt', '--input-format', dest='input_format',
#         default='json',
#         choices=['json', 'text'],
#         help='Format of input data file: "json" or "text" [default: "json"]'
#     )


def add_output_arguments (parser, tool_name):
    """ Add common output directive and file arguments to the given argparse parser object. """
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


# def add_output_format_argument (parser, tool_name):
#     """ Add an output format specification argument to the given argparse parser object. """
#     parser.add_argument(
#         '-ofmt', '--output-format', dest='output_format',
#         default='json',
#         choices=['json', 'other'],
#         help='Output format for results: "json" or "other" [default: "json"]'
#     )


# def add_report_file_argument (parser, tool_name):
#     """ Add a report file argument to the given argparse parser object. """
#     parser.add_argument(
#         '-rf', '--report-file', dest='report_file', metavar='filepath',
#         default=argparse.SUPPRESS,
#         help='File path of file to hold the output report [default: (standard error)]'
#     )


def add_report_format_argument (parser, tool_name):
    """ Add a report format specification argument to the given argparse parser object. """
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


def add_table_name_argument (parser, tool_name, default_msg='no default'):
    """ Add the argument, naming a database table, to the given argparse parser object. """
    parser.add_argument(
        '-tn', '--table-name', dest='table_name', metavar='table-name',
        default=argparse.SUPPRESS,
        help="Table name for data stored in the database [default: {}]".format(default_msg)
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
