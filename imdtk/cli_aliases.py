#!/usr/bin/env python
#
# Module to add aliases (fields) for the header fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 5/30/2020.
#   Last Modified: Initial creation.
#
import os
import sys
import logging as log
import argparse

from config.settings import LOG_LEVEL
from imdtk.core.file_utils import validate_file_path
from imdtk.tools.aliases import DEFAULT_ALIASES_FILEPATH, AliasesTool
from imdtk.tools.i_tool import OUTPUT_EXTENTS


# Program name for this tool.
TOOL_NAME = 'aliases'

# Version of this tool.
VERSION = '0.0.1'


def main (argv=None):
    """
    The main method for the tool. This method is called from the command line,
    processes the command line arguments and calls into the ImdTk library to do its work.
    This main method takes no arguments so it can be called by setuptools.
    """

    # the main method takes no arguments so it can be called by setuptools
    if (argv is None):                      # if called by setuptools
        argv = sys.argv[1:]                 # then fetch the arguments from the system

    # setup logging configuration
    log.basicConfig(level=LOG_LEVEL)

    # setup command line argument parsing
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        formatter_class=argparse.RawTextHelpFormatter,
        description='Add aliases for headers of a metadata structure and output it.'
    )

    parser.add_argument(
        '--version', action='version', version="%(prog)s version {}".format(VERSION),
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

    parser.add_argument(
        '-os', '--output-sink', dest='output_sink', nargs='?',
        default='stdout',
        choices=['file', 'stdout'],
        help='Where to send the results of processing [default: stdout (standard output)]'
    )

    parser.add_argument(
        '-ofmt', '--output-format', dest='output_format',
        default='json',
        choices=['json', 'pickle'],
        help='Output format for results: "json" or "pickle" [default: "json"]'
    )

    parser.add_argument(
        '-a', '--aliases', dest='alias_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help="File of aliases for metadata header fields [default: {}]".format(DEFAULT_ALIASES_FILEPATH)
    )

    parser.add_argument(
        '-if', '--input_file', dest='input_file', metavar='path_to_input_file',
        default=argparse.SUPPRESS,
        help='Path to a readable metadata file containing header fields to be aliased [default: stdin (standard input)]'
    )

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}.main): ARGS={}".format(TOOL_NAME, args))

    # filter the given input file path for validity
    input_file = args.get('input_file')
    if (input_file):                        # if input file given, check it
        if (not validate_file_path(input_file, OUTPUT_EXTENTS)):
            print("({}): A readable, valid input file must be given. Exiting...".format(TOOL_NAME),
                  file=sys.stderr)
            sys.exit(20)

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME
    args['VERSION'] = VERSION

    # call the tool layer to process the given, validated input file
    tool = AliasesTool(args)
    tool.process_and_output()
    tool.cleanup()



if __name__ == "__main__":
    main()
