#!/usr/bin/env python
#
# Module to add aliases (fields) for the column name fields in an Astropy-derived
# catalog information metadata structure.
#   Written by: Tom Hicks. 8/7/2020.
#   Last Modified: Reorder CLI arguments.
#
import argparse
import sys

from config.settings import DEFAULT_CAT_ALIASES_FILEPATH
import imdtk.exceptions as errors
import imdtk.tools.cli_utils as cli_utils
from imdtk.tasks.catalog_aliases import CatalogAliasesTask


# Program name for this tool.
TOOL_NAME = 'catalog_aliases'


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
        description='Add aliases for column names of a catalog metadata structure and output it.'
    )

    cli_utils.add_shared_arguments(parser, TOOL_NAME)
    cli_utils.add_input_file_argument(parser, TOOL_NAME)
    cli_utils.add_aliases_argument(parser, TOOL_NAME, default_msg=DEFAULT_CAT_ALIASES_FILEPATH)
    cli_utils.add_output_arguments(parser, TOOL_NAME)

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("({}.main): ARGS={}".format(TOOL_NAME, args), file=sys.stderr)

    # if input file path given, check the file path for validity
    input_file = args.get('input_file')
    cli_utils.check_input_file(input_file, TOOL_NAME)  # may exit here and not return!

    # if aliases file path given, check the file path for validity
    alias_file = args.get('alias_file')
    cli_utils.check_alias_file(alias_file, TOOL_NAME)  # may exit here and not return!

    # add additional arguments to args
    args['TOOL_NAME'] = TOOL_NAME

    # call the task layer to process the given, validated input file
    try:
        task = CatalogAliasesTask(args)
        task.input_process_output()

    except errors.ProcessingError as pe:
        errMsg = "({}): ERROR: Processing Error ({}): {}".format(
            TOOL_NAME, pe.error_code, pe.message)
        print(errMsg, file=sys.stderr)
        sys.exit(pe.error_code)



if __name__ == "__main__":
    main()
