#!/usr/bin/env python
#
# Python pipeline to extract catalog metadata and create a PostreSQL database table from it.
#   Written by: Tom Hicks. 8/20/20.
#   Last Modified: Reorder CLI arguments.
#
import argparse
import sys

from config.settings import DEFAULT_CAT_ALIASES_FILEPATH
import imdtk.exceptions as errors
import imdtk.tools.cli_utils as cli_utils

from imdtk.tasks.fits_catalog_md import FitsCatalogMetadataTask
from imdtk.tasks.catalog_aliases import CatalogAliasesTask
from imdtk.tasks.fits_catalog_mktbl_sink import FitsCatalogMakeTableSink


# Program name for this tool.
TOOL_NAME = 'fits_cat_mktbl_pipe'


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
        description='Pipeline to extract catalog metadata and create a PostgreSQL database table.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME)
    cli_utils.add_input_file_argument(parser, TOOL_NAME)
    cli_utils.add_fits_file_argument(parser, TOOL_NAME)
    cli_utils.add_catalog_hdu_argument(parser, TOOL_NAME)
    cli_utils.add_aliases_argument(parser, TOOL_NAME, default_msg=DEFAULT_CAT_ALIASES_FILEPATH)
    cli_utils.add_output_arguments(parser, TOOL_NAME)
    cli_utils.add_database_arguments(parser, TOOL_NAME)
    cli_utils.add_catalog_table_argument(parser, TOOL_NAME)

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

    # instantiate the tasks which form the pipeline
    fits_catalog_mdTask = FitsCatalogMetadataTask(args)
    catalog_aliasesTask = CatalogAliasesTask(args)
    fits_catalog_mktbl_sinkTask = FitsCatalogMakeTableSink(args)

    # compose and call the pipeline tasks
    if (args.get('verbose')):
        print("({}): Processing FITS file '{}'.".format(TOOL_NAME, fits_file), file=sys.stderr)

    try:
        fits_catalog_mktbl_sinkTask.output_results(  # sink to DB: nothing returned
            catalog_aliasesTask.process(
                fits_catalog_mdTask.process(None)))  # metadata source

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
