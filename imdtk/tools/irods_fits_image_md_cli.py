#!/usr/bin/env python
#
# Module to extract image metadata from an iRods-resident FITS file and output it as JSON.
#   Written by: Tom Hicks. 10/14/20.
#   Last Modified: Refactor: pass iRods helper in ctor.
#
import argparse
import sys

import imdtk.exceptions as errors
import imdtk.core.fits_utils as fits_utils
import imdtk.tools.cli_utils as cli_utils
from imdtk.core.fits_irods_helper import FitsIRodsHelper
from imdtk.tasks.irods_fits_image_md import IRodsFitsImageMetadataTask


# Program name for this tool.
TOOL_NAME = 'irods_fits_image_md'


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
        description='Extract image metadata from an iRods-resident FITS file and output it as JSON.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME)
    cli_utils.add_hdu_argument(parser, TOOL_NAME)
    cli_utils.add_ignore_list_argument(parser, TOOL_NAME)
    cli_utils.add_output_arguments(parser, TOOL_NAME)
    cli_utils.add_irods_fits_file_argument(parser, TOOL_NAME)

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}.main): ARGS={}".format(TOOL_NAME, args), file=sys.stderr)

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME

    # get the iRods file path argument of the file to be opened
    irff_path = args.get('irods_fits_file')

    # the specified FITS file must have a valid FITS extension
    if (not fits_utils.is_fits_filename(irff_path)):
        errMsg = "A readable, valid FITS image filepath must be specified.".format(irff_path)
        raise errors.ProcessingError(errMsg)

    # get an instance of the iRods accessor class
    firh = FitsIRodsHelper(args)

    # instantiate the task
    task = IRodsFitsImageMetadataTask(args, firh)

    if (args.get('verbose')):
        print("({}): Processing iRods FITS file '{}'.".format(TOOL_NAME, irff_path), file=sys.stderr)

    # call the task layer to process the given, unvalidated remote iRods FITS file
    try:
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

    finally:
        task.cleanup()

    if (args.get('verbose')):
        print("({}): Processed iRods FITS file '{}'.".format(TOOL_NAME, irff_path), file=sys.stderr)


if __name__ == "__main__":
    main()
