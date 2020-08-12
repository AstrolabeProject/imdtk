#!/usr/bin/env python
#
# Module to extract image metadata from a FITS file and output it as JSON.
#   Written by: Tom Hicks. 5/21/2020.
#   Last Modified: Update for renames.
#
import argparse
import sys

import imdtk.exceptions as errors
import imdtk.tools.cli_utils as cli_utils
from imdtk.core.fits_utils import FITS_IGNORE_KEYS
from imdtk.tasks.fits_image_md import FitsImageMetadataTask


# Program name for this tool.
TOOL_NAME = 'fits_image_md'


def main (argv=None):
    """
    The main method for the tool. This method is called from the command line,
    processes the command line arguments and calls into the ImdTk library to do its work.
    This main method takes no arguments so it can be called by setuptools.
    """

    # the main method takes no arguments so it can be called by setuptools
    if (argv is None):                      # if called by setuptools
        argv = sys.argv[1:]                 # then fetch the arguments from the system

    # setup command line argument parsing and add shared arguments
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        formatter_class=argparse.RawTextHelpFormatter,
        description='Extract image metadata from a FITS file and output it as JSON.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME)
    cli_utils.add_output_arguments(parser, TOOL_NAME)
    cli_utils.add_fits_file_arguments(parser, TOOL_NAME)

    # add arguments specific to this module
    parser.add_argument(
        '-ig', '--ignore', dest='ignore_list', action="append", metavar='header_key_to_ignore',
        default=argparse.SUPPRESS,
        help="Single header key to ignore (may repeat). [default: {} ]".format(FITS_IGNORE_KEYS)
    )

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}.main): ARGS={}".format(TOOL_NAME, args), file=sys.stderr)

    # check the required FITS file path for validity
    fits_file = args.get('fits_file')
    cli_utils.check_fits_file(fits_file, TOOL_NAME)  # may system exit here and not return!

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME

    # call the task layer to process the given, validated FITS file
    if (args.get('verbose')):
        print("({}): Processing FITS file '{}'.".format(TOOL_NAME, fits_file), file=sys.stderr)

    try:
        task = FitsImageMetadataTask(args)
        task.process_and_output()

    except errors.UnsupportedTypeError as ute:
        errMsg = "({}): INFO: Unsupported File Type ({}): {}".format(
            TOOL_NAME, ute.error_code, ute.message)
        print(errMsg, file=sys.stderr)
        sys.exit(ute.error_code)

    except errors.ProcessingError as pe:
        errMsg = "({}): ERROR: Processing Error ({}): {}".format(
            TOOL_NAME, pe.error_code, pe.message)
        print(errMsg, file=sys.stderr)
        sys.exit(pe.error_code)

    if (args.get('verbose')):
        print("({}): Processed FITS file '{}'.".format(TOOL_NAME, fits_file), file=sys.stderr)


if __name__ == "__main__":
    main()
