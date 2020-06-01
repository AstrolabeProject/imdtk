#!/usr/bin/env python
#
# Module to extract image metadata from a FITS file and output it as JSON.
#   Written by: Tom Hicks. 5/21/2020.
#   Last Modified: Rename module. Use new CLI utils module. Increment version number.
#
import os
import sys
import logging as log
import argparse

import imdtk.cli_utils as cli_utils
from config.settings import LOG_LEVEL
from imdtk.core.file_utils import validate_file_path
from imdtk.core.fits_utils import FITS_EXTENTS, FITS_IGNORE_KEYS
from imdtk.tools.headers import HeadersSourceTool


# Program name for this tool.
TOOL_NAME = 'headers'

# Version of this tool.
VERSION = '0.0.3'


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

    cli_utils.add_shared_arguments(parser, TOOL_NAME, VERSION, has_input_file=False)
    cli_utils.add_output_arguments(parser, TOOL_NAME, VERSION)

    # add arguments specific to this module
    parser.add_argument(
        '-hdu', '--hdu', dest='which_hdu', metavar='HDU_index',
        default=0,
        help='Index of HDU containing the metadata [default: 0 (the first)]'
    )

    parser.add_argument(
        '-ig', '--ignore', dest='ignore_list', action="append", metavar='header_key_to_ignore',
        default=argparse.SUPPRESS,
        help="Single header key to ignore (may repeat). [default: {} ]".format(FITS_IGNORE_KEYS)
    )

    parser.add_argument(
        '-ff', '--fits_file', dest='fits_file', required=True, metavar='path_to_image_file',
        help='Path to a readable FITS image file from which to extract metadata [required]'
    )

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}.main): ARGS={}".format(TOOL_NAME, args))

    # filter the given FITS file path for validity
    fits_file = args.get('fits_file')
    if (not validate_file_path(fits_file, FITS_EXTENTS)):
        print("({}): A readable, valid FITS image file must be given. Exiting...".format(TOOL_NAME),
              file=sys.stderr)
        sys.exit(20)

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME
    args['VERSION'] = VERSION

    # call the tool layer to process the given, validated FITS file
    tool = HeadersSourceTool(args)
    tool.process_and_output()
    tool.cleanup()



if __name__ == "__main__":
    main()
