#!/usr/bin/env python
#
# Python pipeline to extract image metadata from FITS images in an iRods directory,
# storing the metadata into a PostreSQL database.
#   Written by: Tom Hicks. 11/22/20.
#   Last Modified: More cleanup on fits irods helper.
#
import argparse
import sys

import imdtk.exceptions as errors
import imdtk.tools.cli_utils as cli_utils

from imdtk.core.fits_irods_helper import FitsIRodsHelper
from imdtk.core.fits_utils import gen_fits_file_paths
from imdtk.tasks.fields_info import FieldsInfoTask
from imdtk.tasks.image_aliases import ImageAliasesTask
from imdtk.tasks.irods_fits_image_md import IRodsFitsImageMetadataTask
from imdtk.tasks.irods_jwst_oc_calc import IRods_JWST_ObsCoreCalcTask
from imdtk.tasks.jwst_pgsql_sink import JWST_ObsCorePostgreSQLSink
from imdtk.tasks.miss_report import MissingFieldsTask


# Program name for this tool.
TOOL_NAME = 'irods_mmd_pgsql_pipe'


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
        description='Pipeline to extract image metadata from iRods FITS files and store into a PostreSQL database.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME)
    cli_utils.add_input_dir_argument(parser, TOOL_NAME)
    cli_utils.add_hdu_argument(parser, TOOL_NAME)
    cli_utils.add_ignore_list_argument(parser, TOOL_NAME)
    cli_utils.add_aliases_argument(parser, TOOL_NAME)
    cli_utils.add_fields_info_argument(parser, TOOL_NAME)
    cli_utils.add_collection_argument(parser, TOOL_NAME)
    cli_utils.add_report_format_argument(parser, TOOL_NAME)
    cli_utils.add_output_arguments(parser, TOOL_NAME)
    cli_utils.add_database_arguments(parser, TOOL_NAME)
    cli_utils.add_table_name_argument(parser, TOOL_NAME)

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}.main): ARGS={}".format(TOOL_NAME, args), file=sys.stderr)

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME

    # get an instance of the iRods accessor class
    firh = FitsIRodsHelper(args)

    # instantiate the tasks which form the pipeline
    irods_fits_image_mdTask = IRodsFitsImageMetadataTask(args, firh)
    image_aliasesTask = ImageAliasesTask(args)
    fields_infoTask = FieldsInfoTask(args)
    irods_jwst_oc_calcTask = IRods_JWST_ObsCoreCalcTask(args, firh)
    miss_reportTask = MissingFieldsTask(args)
    jwst_pgsql_sinkTask = JWST_ObsCorePostgreSQLSink(args)

    # get and check the required image directory path for validity
    input_dir = args.get('input_dir')
    if (not firh.collection_exists(input_dir)):
        firh.cleanup()                            # cleanup resources opened here
        cli_utils.irods_input_dir_exit(TOOL_NAME, input_dir)  # error exit out here: never returns

    # make of list of absolute iRods file paths pointing to FITS files
    ir_dir = firh.getc(input_dir, absolute=True)
    irff_paths = [fpath for fpath in firh.gen_fits_file_paths(ir_dir)]

    # call the pipeline on each FITS file in the input directory:
    if (args.get('verbose')):
        print("({}): Processing FITS files in '{}'.".format(TOOL_NAME, input_dir), file=sys.stderr)

    proc_count = 0                                # initialize count of processed files
    for irff_path in irff_paths:
        args['irods_fits_file'] = irff_path       # reset the FITS file argument to next file

        if (args.get('verbose')):
            print("({}): Processing FITS file '{}'.".format(TOOL_NAME, irff_path), file=sys.stderr)

        try:
            jwst_pgsql_sinkTask.output_results(   # sink: nothing returned
                miss_reportTask.process(          # report: passes data through
                    irods_jwst_oc_calcTask.process(
                        fields_infoTask.process(
                            image_aliasesTask.process(
                                irods_fits_image_mdTask.process(None))))))  # metadata source

            proc_count += 1                       # increment count of processed files

        except errors.UnsupportedTypeError as ute:
            errMsg = "({}): WARNING: Unsupported File Type ({}): {}".format(
                TOOL_NAME, ute.error_code, ute.message)
            print(errMsg, file=sys.stderr)

        except errors.ProcessingError as pe:
            errMsg = "({}): ERROR: Processing Error ({}): {}".format(
                TOOL_NAME, pe.error_code, pe.message)
            print(errMsg, file=sys.stderr)

    # call cleanup method for tasks which opened resources
    jwst_pgsql_sinkTask.cleanup()
    irods_jwst_oc_calcTask.cleanup()
    irods_fits_image_mdTask.cleanup()
    firh.cleanup()                          # cleanup resources opened here


    if (args.get('verbose')):
        print("({}): Processed iRods {} FITS files.".format(TOOL_NAME, proc_count), file=sys.stderr)



if __name__ == "__main__":
    main()
