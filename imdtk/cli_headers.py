#!/usr/bin/env python
#
# Module to extract image metadata from a FITS file and output it as JSON.
#   Written by: Tom Hicks. 5/21/2020.
#   Last Modified: Initial creation.
#
import os
import sys
import logging as log
import argparse

from astropy.io import fits

from imdtk.core.file_utils import validate_file_path
from imdtk.core.fits_utils import FITS_EXTENTS
import imdtk.tools.headers as headers


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
        description='Extract image metadata from a FITS file and output it as JSON.'
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
        '-i', '--ignore', dest='ignore_list', action="append", metavar='header_key_to_ignore',
        default=argparse.SUPPRESS,
        help="Single header key to ignore (may repeat). [default: {} ]".format(headers.FITS_IGNORE_KEYS)
    )

    parser.add_argument(
        '--version', action='version', version="%(prog)s version {}".format(VERSION),
        help='Show version information and exit.'
    )

    parser.add_argument(
        '-f', '--file', dest='image_path', required=True, metavar='path_to_image_file',
        help='Path to a FITS image file from which to extract metadata [required]'
    )

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    print("ARGS={}".format(args))           # REMOVE LATER

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("(cli_headers.main): args={}".format(args))

    # filter the given input paths for validity, removing invalid paths
    file_path = args.get('image_path')
    if ((not file_path) or (not validate_file_path(file_path, FITS_EXTENTS))):
        print("(cli_headers): At least one existing, readable FITS image file must be given. Exiting...", file=sys.stderr)
        sys.exit(20)

    # process the given, validated FITS file
    if (args.get('verbose')):
        log.info("(cli_headers): Processing FITS file '{}'".format(file_path))

    try:
        with fits.open(file_path) as hdus_list:
            hdrs = headers.get_header_fields(hdus_list,
                                             which_hdu=args.get('which_hdu'),
                                             ignore=args.get('ignore_list'))
            if (hdrs is None):
                print("(cli_headers): Unable to read metadata from FITS file '{}'.".format(file_path), file=sys.stderr)
                sys.exit(21)

            print("HEADERS: {}".format(hdrs)) # REMOVE LATER

            # TODO: IMPLEMENT WRITING OUTPUT AS JSON


    except Exception as ex:
        print("(cli_headers): Exception while reading metadata from FITS file '{}': {}".format(file_path, ex), file=sys.stderr)
        sys.exit(22)




if __name__ == "__main__":
    main()
