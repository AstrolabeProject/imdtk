#!/usr/bin/env python
#
# Module to add aliases (fields) for the header fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 5/30/2020.
#   Last Modified: Update for rename to task.
#
import os, sys
import logging as log
import argparse

import imdtk.cli_utils as cli_utils
from config.settings import LOG_LEVEL
from imdtk.core.file_utils import good_file_path
from imdtk.tools.aliases import DEFAULT_ALIASES_FILEPATH, AliasesTask
from imdtk.tools.i_tool import OUTPUT_EXTENTS


# Program name for this tool.
TOOL_NAME = 'aliases'

# Version of this tool.
VERSION = '0.2.0'


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

    # setup command line argument parsing and add shared arguments
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        formatter_class=argparse.RawTextHelpFormatter,
        description='Add aliases for headers of a metadata structure and output it.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_output_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_input_arguments(parser, TOOL_NAME, VERSION)

    # add arguments specific to this module
    parser.add_argument(
        '-a', '--aliases', dest='alias_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help="File of aliases for metadata header fields [default: {}]".format(DEFAULT_ALIASES_FILEPATH)
    )

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}.main): ARGS={}".format(TOOL_NAME, args), file=sys.stderr)

    # filter the given input file path for validity
    input_file = args.get('input_file')
    if (input_file):                        # if input file given, check it
        if (not good_file_path(input_file)):
            print("({}): A readable, valid input file must be given. Exiting...".format(TOOL_NAME),
                  file=sys.stderr)
            sys.exit(20)

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME
    args['VERSION'] = VERSION

    # call the tool layer to process the given, validated input file
    tool = AliasesTask(args)
    tool.process_and_output()
    tool.cleanup()



if __name__ == "__main__":
    main()
