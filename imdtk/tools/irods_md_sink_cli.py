#!/usr/bin/env python
#
# Module to sink incoming metadata by attaching it to an iRods file.
#   Written by: Tom Hicks. 12/20/20.
#   Last Modified: Add capability to just remove metadata items. Call cleanup on fits irods helper.
#
import argparse
import sys

import imdtk.exceptions as errors
import imdtk.tools.cli_utils as cli_utils

from imdtk.core.fits_irods_helper import FitsIRodsHelper
from imdtk.tasks.irods_md_sink import IRodsMetadataSink


# Program name for this tool.
TOOL_NAME = 'irods_md_sink'


def main (argv=None):
    """
    The main method for the pipeline. This method is called from the command line,
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
        description='Read incoming metadata and attach it to an iRods file as iRods metadata.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME)
    cli_utils.add_input_file_argument(parser, TOOL_NAME)
    cli_utils.add_irods_md_file_argument(parser, TOOL_NAME)

    # add arguments specific to this module
    parser.add_argument(
        '-rm', '--remove', dest='remove_only', action='store_true',
        default=False,
        help='If True, remove matching input items from iRods file metadata [default: False].'
    )

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

    # get an instance of the iRods accessor class
    firh = FitsIRodsHelper(args)

    # compose and call the pipeline tasks
    try:
        task = IRodsMetadataSink(args, firh)
        task.input_process_output()

    except errors.UnsupportedType as ute:
        errMsg = "({}): WARNING: Unsupported File Type ({}): {}".format(
            TOOL_NAME, ute.error_code, ute.message)
        print(errMsg, file=sys.stderr)
        sys.exit(ute.error_code)

    except errors.ProcessingError as pe:
        errMsg = "({}): ERROR: Processing Error ({}): {}".format(
            TOOL_NAME, pe.error_code, pe.message)
        print(errMsg, file=sys.stderr)
        sys.exit(pe.error_code)

    finally:
        task.cleanup()                      # cleanup any task resources
        firh.cleanup()                      # cleanup resources opened here



if __name__ == "__main__":
    main()
