#!/usr/bin/env python
#
# Module to extract a catalog data table from a FITS file and output it as JSON.
#   Written by: Tom Hicks. 8/12/2020.
#   Last Modified: Warn on unsupported file type error.
#
import argparse
import sys

import imdtk.exceptions as errors
import imdtk.tools.cli_utils as cli_utils
from imdtk.tasks.fits_catalog_data import FitsCatalogDataTask


# Program name for this tool.
TOOL_NAME = 'fits_catalog_data'


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
        description='Extract a catalog data table from a FITS file and output it as JSON.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME)
    cli_utils.add_fits_file_argument(parser, TOOL_NAME)
    cli_utils.add_catalog_hdu_argument(parser, TOOL_NAME)
    cli_utils.add_output_arguments(parser, TOOL_NAME)

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
        task = FitsCatalogDataTask(args)
        task.process_and_output()

    except errors.UnsupportedTypeError as ute:
        errMsg = "({}): WARNING: Unsupported File Type ({}): {}".format(
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
