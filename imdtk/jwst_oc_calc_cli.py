#!/usr/bin/env python
#
# Module to calculate values for the ObsCore fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/11/2020.
#   Last Modified: Increment version to 0.7.0.
#
import os, sys
import logging as log
import argparse

import imdtk.cli_utils as cli_utils
from config.settings import LOG_LEVEL
from imdtk.tasks.jwst_oc_calc import JWST_ObsCoreCalcTask


# Program name for this tool.
TOOL_NAME = 'jwst_oc_calc'

# Version of this tool.
VERSION = '0.7.0'


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
        description='Extract image metadata from a FITS file and output it as JSON.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_output_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_input_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_fits_file_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_collection_arguments(parser, TOOL_NAME, VERSION)

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}.main): ARGS={}".format(TOOL_NAME, args), file=sys.stderr)

    # if input file path given, check the file path for validity
    input_file = args.get('input_file')
    cli_utils.check_input_file(input_file, TOOL_NAME) # may system exit here and not return!

    # check the required FITS file path for validity
    fits_file = args.get('fits_file')
    cli_utils.check_fits_file(fits_file, TOOL_NAME) # may system exit here and not return!

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME
    args['VERSION'] = VERSION

    # call the task layer to process the given, validated files
    tool = JWST_ObsCoreCalcTask(args)
    tool.input_process_output()
    tool.cleanup()



if __name__ == "__main__":
    main()
