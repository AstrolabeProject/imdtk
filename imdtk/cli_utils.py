#
# Class defining utility methods for tool components CLI.
#   Written by: Tom Hicks. 6/1/2020.
#   Last Modified: Add input and support filepath validation methods.
#                  Import default aliases and fields info filepaths as default argparse messages.
#
import os, sys
import argparse

from config.settings import DEFAULT_ALIASES_FILEPATH, DEFAULT_FIELDS_FILEPATH
from imdtk.core.file_utils import good_file_path, validate_file_path
from imdtk.core.fits_utils import FITS_EXTENTS


def add_aliases_arguments (parser, tool_name, version, default_msg=DEFAULT_ALIASES_FILEPATH):
    """ Add the argument(s) related to parsing information from aliases files
        to the given argparse parser object. """
    parser.add_argument(
        '-a', '--aliases', dest='alias_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help="File of aliases for metadata header fields [default: {}]".format(default_msg)
    )


def add_collection_arguments (parser, tool_name, version, default_msg='no default'):
    """ Add the argument(s) related to collection specification
        to the given argparse parser object. """
    parser.add_argument(
        '-c', '--collection', dest='collection', metavar='collection-name',
        default=argparse.SUPPRESS,
        help="Collection name for ingested images [default: {}]".format(default_msg)
    )


def add_fields_info_arguments (parser, tool_name, version, default_msg=DEFAULT_FIELDS_FILEPATH):
    """ Add the argument(s) related to parsing information from fields information files
        to the given argparse parser object. """
    parser.add_argument(
        '-fi', '--fields-info', dest='fields_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help="Field information file for fields to be processed [default: {}]".format(default_msg)
    )


def add_fits_file_arguments (parser, tool_name, version):
    """ Add the argument(s) related to parsing information from FITS files
        to the given argparse parser object. """
    parser.add_argument(
        '-hdu', '--hdu', dest='which_hdu', metavar='HDU_index',
        default=0,
        help='Index of HDU containing the metadata [default: 0 (the first)]'
    )

    parser.add_argument(
        '-ff', '--fits_file', dest='fits_file', required=True, metavar='path_to_image_file',
        help='Path to a readable FITS image file from which to extract metadata [required]'
    )


def add_input_arguments (parser, tool_name, version):
    """ Add common input arguments to the given argparse parser object. """
    parser.add_argument(
        '-ifmt', '--input-format', dest='input_format',
        default='json',
        choices=['json', 'text'],
        help='Format of input data file: "json" or "text" [default: "json"]'
    )

    parser.add_argument(
        '-if', '--input_file', dest='input_file', metavar='path_to_input_file',
        default=argparse.SUPPRESS,
        help='Path to a readable data file to be processed [default: (standard input)]'
    )


def add_output_arguments (parser, tool_name, version):
    """ Add common output arguments to the given argparse parser object. """
    parser.add_argument(
        '-g', '--generate', dest='gen_file_path', action='store_true',
        default=False,
        help='Automatically generate the output filename and path. [default: False].'
    )

    # parser.add_argument(
    #     '-os', '--output-sink', dest='output_sink', nargs='?',
    #     default='stdout',
    #     choices=['file', 'genfile', 'stdout'],
    #     help='Where to send the results of processing [default: stdout (standard output)]'
    # )

    parser.add_argument(
        '-of', '--output_file', dest='output_file', metavar='path_to_output_file',
        default=argparse.SUPPRESS,
        help='File path of file to hold the processing results [default: (standard output)]'
    )

    # parser.add_argument(
    #     '-ofmt', '--output-format', dest='output_format',
    #     default='json',
    #     choices=['json', 'other'],
    #     help='Output format for results: "json" or "other" [default: "json"]'
    # )


def add_report_arguments (parser, tool_name, version):
    # parser.add_argument(
    #     '-rf', '--report_file', dest='report_file', metavar='path_to_report_file',
    #     default=argparse.SUPPRESS,
    #     help='File path of file to hold the output report [default: (standard error)]'
    # )

    parser.add_argument(
        '-rfmt', '--report-format', dest='report_format',
        default='text',
        choices=['json', 'text'],
        help='Output format for reports: "json" or "text" [default: "text"]'
    )


def add_shared_arguments (parser, tool_name, version):
    """ Add the arguments shared by all tools to the given argparse parser object. """
    parser.add_argument(
        '--version', action='version', version="{} version {}".format(tool_name, version),
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


def check_alias_file (alias_file, tool_name, exit_code=22):
    """
    If a path to an aliases file is given, check that it is a good path. If not, then exit
    the entire program here with the specified (or default) system exit code.
    """
    if (alias_file):                        # if aliases file given, check it
        if (not good_file_path(alias_file)):
            errMsg = "({}): A readable aliases file must be specified. Exiting...".format(TOOL_NAME)
            log.error(errMsg)
            print(errMsg, file=sys.stderr)
            sys.exit(exit_code)


def check_fields_file (fields_file, tool_name, exit_code=23):
    """
    If a path to an aliases file is given, check that it is a good path. If not, then exit
    the entire program here with the specified (or default) system exit code.
    """
    if (fields_file):                       # if fields info file given, check it
        if (not good_file_path(fields_file)):
            errMsg = "({}): A readable fields information file must be specified. Exiting...".format(TOOL_NAME)
            log.error(errMsg)
            print(errMsg, file=sys.stderr)
            sys.exit(exit_code)


def check_fits_file (fits_file, tool_name, exit_code=21):
    """
    Check that the required FITS file path is a valid path. If not, then exit
    the entire program here with the specified (or default) system exit code.
    """
    if (not validate_file_path(fits_file, FITS_EXTENTS)):
        errMsg = "({}): A readable, valid FITS image file must be specified. Exiting...".format(TOOL_NAME)
        log.error(errMsg)
        print(errMsg, file=sys.stderr)
        sys.exit(exit_code)


def check_input_file (input_file, tool_name, exit_code=20):
    """
    If an input file path is given, check that it is a good path. If not, then exit
    the entire program here with the specified (or default) system exit code.
    """
    if (input_file):                        # if input file given, check it
        if (not good_file_path(input_file)):
            errMsg = "({}): A readable, valid input data file must be specified. Exiting...".format(TOOL_NAME)
            log.error(errMsg)
            print(errMsg, file=sys.stderr)
            sys.exit(exit_code)
