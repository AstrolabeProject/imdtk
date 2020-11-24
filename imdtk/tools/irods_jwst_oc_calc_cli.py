#!/usr/bin/env python
#
# Module to calculate values for the ObsCore fields from metadata derived from an iRods-resident FITS file.
#   Written by: Tom Hicks. 1/20/20.
#   Last Modified: Call CLI exit instead of error.
#
import argparse
import sys

import imdtk.exceptions as errors
import imdtk.core.fits_utils as fits_utils
import imdtk.tools.cli_utils as cli_utils
from imdtk.core.fits_irods_helper import FitsIRodsHelper
from imdtk.tasks.irods_jwst_oc_calc import IRods_JWST_ObsCoreCalcTask


# Program name for this tool.
TOOL_NAME = 'irods_jwst_oc_calc'


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
        description='Calculate ObsCore values from incoming metadata and an iRods FITS file, add the calculated fields to the metadata structure, and output it.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME)
    cli_utils.add_input_file_argument(parser, TOOL_NAME)
    cli_utils.add_irods_fits_file_argument(parser, TOOL_NAME)
    cli_utils.add_hdu_argument(parser, TOOL_NAME)
    cli_utils.add_collection_argument(parser, TOOL_NAME)
    cli_utils.add_output_arguments(parser, TOOL_NAME)

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}.main): ARGS={}".format(TOOL_NAME, args), file=sys.stderr)

    # if input file path given, check the file path for validity
    input_file = args.get('input_file')
    cli_utils.check_input_file(input_file, TOOL_NAME)  # may system exit here and not return!

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME

    # get the iRods file path argument of the file to be opened
    irff_path = args.get('irods_fits_file')

    # the specified FITS file must have a valid FITS extension
    if (not fits_utils.is_fits_filename(irff_path)):
        cli_utils.fits_file_exit(TOOL_NAME, irff_path)  # error exit out here: never returns

    # get an instance of the iRods accessor class
    firh = FitsIRodsHelper(args)

    # instantiate the task
    task = IRods_JWST_ObsCoreCalcTask(args, firh)

    if (args.get('verbose')):
        print("({}): Processing iRods FITS file '{}'.".format(TOOL_NAME, irff_path), file=sys.stderr)

    # call task layer to process the input stream using the unvalidated remote iRods FITS file
    try:
        task.input_process_output()

    except errors.ProcessingError as pe:
        errMsg = "({}): ERROR: Processing Error ({}): {}".format(
            TOOL_NAME, pe.error_code, pe.message)
        print(errMsg, file=sys.stderr)
        sys.exit(pe.error_code)

    finally:
        task.cleanup()



if __name__ == "__main__":
    main()
