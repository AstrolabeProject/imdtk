#!/usr/bin/env python
#
# Module to extract an image table from a FITS file and output it as JSON.
#   Written by: Tom Hicks. 7/6/2020.
#   Last Modified: Update for tools package.
#
import argparse
import logging as log
import os
import sys

import imdtk.tools.cli_utils as cli_utils
from config.settings import LOG_LEVEL
from imdtk.tasks.fits_table import FitsTableSourceTask


# Program name for this tool.
TOOL_NAME = 'fits_table'

# Version of this tool.
VERSION = '0.10.0'


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
    cli_utils.add_fits_file_arguments(parser, TOOL_NAME, VERSION)

    # add arguments specific to this module
    parser.add_argument(
        '-thdu', '--table_hdu', dest='table_hdu', metavar='HDU_index',
        default=1,
        help='Index of HDU containing the table data [default: 1 (the second)]'
    )

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}.main): ARGS={}".format(TOOL_NAME, args), file=sys.stderr)

    # check the required FITS file path for validity
    fits_file = args.get('fits_file')
    cli_utils.check_fits_file(fits_file, TOOL_NAME) # may system exit here and not return!

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME
    args['VERSION'] = VERSION

    # call the task layer to process the given, validated FITS file
    tool = FitsTableSourceTask(args)
    tool.process_and_output()



if __name__ == "__main__":
    main()
