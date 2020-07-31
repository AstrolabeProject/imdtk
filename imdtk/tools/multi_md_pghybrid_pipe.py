#!/usr/bin/env python
#
# Python pipeline to extract image metadata from each FITS images in a directory, storing
# the metadata into a Hybrid PostreSQL/JSON database.
#   Written by: Tom Hicks. 7/20/2020.
#   Last Modified: Initial creation.
#
import argparse
import sys

from config.settings import DEFAULT_HYBRID_TABLE_NAME
import imdtk.exceptions as errors
import imdtk.tools.cli_utils as cli_utils
from imdtk.core.fits_utils import FITS_IGNORE_KEYS, gen_fits_file_paths
from imdtk.tasks.aliases import AliasesTask
from imdtk.tasks.fields_info import FieldsInfoTask
from imdtk.tasks.fits_headers import FitsHeadersSourceTask
from imdtk.tasks.jwst_oc_calc import JWST_ObsCoreCalcTask
from imdtk.tasks.jwst_pghybrid_sink import JWST_HybridPostgreSQLSink
from imdtk.tasks.miss_report import MissingFieldsTask


# Program name for this tool.
TOOL_NAME = 'multi_md_pghybrid_pipe'

# Version of this tool.
VERSION = '0.11.0'


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
        description='Pipeline to extract image metadata and store it into a hybrid PostreSQL/JSON database.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_output_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_input_dir_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_hdu_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_fields_info_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_collection_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_report_arguments(parser, TOOL_NAME, VERSION)
    cli_utils.add_database_arguments(parser, TOOL_NAME, VERSION, table_msg=DEFAULT_HYBRID_TABLE_NAME)

    # add arguments specific to this pipeline
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

    # check the required image directory path for validity
    input_dir = args.get('input_dir')
    cli_utils.check_input_dir(input_dir, TOOL_NAME)  # may system exit here and not return!

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME
    args['VERSION'] = VERSION

    # instantiate the tasks which form the pipeline
    fits_headersTask = FitsHeadersSourceTask(args)
    aliasesTask = AliasesTask(args)
    fields_infoTask = FieldsInfoTask(args)
    jwst_oc_calcTask = JWST_ObsCoreCalcTask(args)
    miss_reportTask = MissingFieldsTask(args)
    jwst_pghybrid_sinkTask = JWST_HybridPostgreSQLSink(args)

    # call the pipeline on each FITS file in the input directory:
    if (args.get('verbose')):
        print("({}): Processing FITS files in '{}'.".format(TOOL_NAME, input_dir), file=sys.stderr)

    proc_count = 0                                # initialize count of processed files

    for img_file in gen_fits_file_paths(input_dir):
        args['fits_file'] = img_file              # reset the FITS file argument to next file

        if (args.get('verbose')):
            print("({}): Processing FITS file '{}'.".format(TOOL_NAME, img_file), file=sys.stderr)

        try:
            jwst_pghybrid_sinkTask.output_results(  # sink: nothing returned
                miss_reportTask.process(          # report: passes data through
                    jwst_oc_calcTask.process(
                        fields_infoTask.process(
                            aliasesTask.process(
                                fits_headersTask.process(None))))))  # metadata source

            proc_count += 1                       # increment count of processed files

        except errors.UnsupportedTypeError as ute:
            errMsg = "({}): INFO: Unsupported File Type ({}): {}".format(
                TOOL_NAME, ute.error_code, ute.message)
            print(errMsg, file=sys.stderr)

        except errors.ProcessingError as pe:
            errMsg = "({}): ERROR: Processing Error ({}): {}".format(
                TOOL_NAME, pe.error_code, pe.message)
            print(errMsg, file=sys.stderr)

    if (args.get('verbose')):
        print("({}): Processed {} FITS files.".format(TOOL_NAME, proc_count), file=sys.stderr)



if __name__ == "__main__":
    main()
