#!/usr/bin/env python
#
# Module to add information about desired fields to the FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/9/20.
#   Last Modified: Get default file paths from config/settings.
#
import os, sys
import logging as log
import argparse

import imdtk.cli_utils as cli_utils
from config.settings import LOG_LEVEL, DEFAULT_FIELDS_FILEPATH
from imdtk.core.file_utils import good_file_path
from imdtk.tasks.fields_info import FieldsInfoTask


# Program name for this tool.
TOOL_NAME = 'fields_info'

# Version of this tool.
VERSION = '0.3.0'


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
        description='Add information about desired fields to a metadata structure and output it.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_output_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_input_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_fields_info_arguments(parser, TOOL_NAME, VERSION, DEFAULT_FIELDS_FILEPATH)

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

    # call the task layer to process the given, validated input file
    tool = FieldsInfoTask(args)
    tool.input_process_output()
    tool.cleanup()



if __name__ == "__main__":
    main()
