#!/usr/bin/env python
#
# Module to extract image metadata from a FITS file and output it as JSON.
#   Written by: Tom Hicks. 5/21/2020.
#   Last Modified: Different call for ignore_list. Use tool name in messages. Use raw help formatting.
#
import os
import sys
import logging as log
import argparse

from astropy.io import fits

from imdtk.core.file_utils import validate_file_path
import imdtk.core.fits_utils as fits_utils


# Program name for this tool.
TOOL_NAME = 'headers'

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

    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        formatter_class=argparse.RawTextHelpFormatter,
        description='Extract image metadata from a FITS file and output it as JSON.'
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
        '-hdu', '--hdu', dest='which_hdu', metavar='HDU_index', default=0,
        help='Index of HDU containing the metadata [default: 0 (the first)]'
    )

    parser.add_argument(
        '-ig', '--ignore', dest='ignore_list', action="append", metavar='header_key_to_ignore',
        default=argparse.SUPPRESS,
        help="Single header key to ignore (may repeat). [default: {} ]".format(fits_utils.FITS_IGNORE_KEYS)
    )

    parser.add_argument(
        '-of', '--output-format', dest='output_format',
        default='json',
        choices=['json', 'pickle'],
        help='Output format for results: "json" or "pickle" [default: "json"]'
    )

    parser.add_argument(
        '-f', '--file', dest='image_path', required=True, metavar='path_to_image_file',
        help='Path to a readable FITS image file from which to extract metadata [required]'
    )

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}): ARGS={}".format(TOOL_NAME, args))

    # filter the given input file path for validity
    file_path = args.get('image_path')
    if (not validate_file_path(file_path, fits_utils.FITS_EXTENTS)):
        print("({}): A readable, valid FITS image file must be given. Exiting...".format(TOOL_NAME),
              file=sys.stderr)
        sys.exit(20)

    # process the given, validated FITS file
    if (args.get('verbose')):
        log.info("({}): Processing FITS file '{}'".format(TOOL_NAME, file_path))

    which_hdu = args.get('which_hdu', 0)
    ignore_list = args.get('ignore_list', [])

    try:
        with fits.open(file_path) as hdus_list:
            if (ignore_list):
                hdrs = fits_utils.get_header_fields(hdus_list, which_hdu, ignore_list)
            else:
                hdrs = fits_utils.get_header_fields(hdus_list, which_hdu)

            if (hdrs is None):
                print("({}): Unable to read metadata from FITS file '{}'.".format(TOOL_NAME, file_path),
                      file=sys.stderr)
                sys.exit(21)

            print("HEADERS: {}".format(hdrs)) # REMOVE LATER

            # TODO: IMPLEMENT WRITING OUTPUT AS JSON


    except Exception as ex:
        print("({}): Exception while reading metadata from FITS file '{}': {}.".format(TOOL_NAME, file_path, ex), file=sys.stderr)
        sys.exit(22)



if __name__ == "__main__":
    main()
