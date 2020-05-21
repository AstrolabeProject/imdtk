#!/usr/bin/env python
#
# Module to extract image metadata from  FITS files and load it into a database table.
#   Written by: Tom Hicks. 2/19/2020.
#   Last Modified: Make output directory argument a setting.
#
import os
import sys
import logging as log
import argparse

from config.settings import PROGRAM_NAME
from imdtk.core.file_utils import good_dir_path, good_file_path, validate_file_path, validate_path_strings
from imdtk.core.fits_utils import FITS_EXTENTS
from imdtk.core.jwst_processor import JwstProcessor
from imdtk.version import VERSION


def check_filepath (filepath, file_desc=''):
    """
    Check the given filepath for validity, as follows:
      if given None skip testing, return True
      if given a path to a readable file, return True
      else log and print an error message and return False
    """
    if ((filepath is None) or good_file_path(filepath)): # skip testing if no filepath given
        return True
    else:
        errMsg = "Unable to find and read the specified {0} file '{1}'".format(file_desc, filepath)
        # log.error(errMsg)
        print(errMsg, file=sys.stderr)
        return False


def process_dirs (processor, root_dir):
    """ Recursively find and process the FITS files in the given root directory.
        Return a count of the files successfully processed.
    """
    count = 0
    for dirpath, _, files in os.walk(root_dir, followlinks=True):
        if (good_dir_path(dirpath)):
            for afile in files:
                img_file = os.path.join(dirpath, afile)
                if (validate_file_path(img_file, FITS_EXTENTS)):
                    count += processor.process_a_file(img_file)
    return count



def main (argv=None):
    """
    The main method for the ImdEx program. This method is called from the command line,
    processes the command line arguments and calls into the ImdEx library to do its work.
    This method takes no arguments so it can be called by setuptools.
    """

    # the main method takes no arguments so it can be called by setuptools
    if (argv is None):                      # if called by setuptools
        argv = sys.argv[1:]                 # then fetch the arguments from the system

    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description='Extract image metadata from FITS files and load it into a database table.'
    )

    parser.add_argument(
        '-a', '--aliases', dest='alias_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help='File of aliases (FITS keyword to ObsCore keyword mappings) [default: "/imdtk/config/jwst-aliases.ini"]'
    )

    parser.add_argument(
        '-c', '--collection', dest='collection', metavar='collection-name',
        default=argparse.SUPPRESS,
        help='Collection name for ingested images [no default]'
    )

    parser.add_argument(
        '-d', '--debug', dest='debug', action='store_true',
        default=False,
        help='Print debugging output during processing [default: non-debug mode]'
    )

    parser.add_argument(
        '-db', '--dbconfig', dest='db_config_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help='Database configuration properties file [default: "/imdtk/config/jwst-dbconfig.ini"]'
    )

    parser.add_argument(
        '-fi', '--field-info', dest='fields_file', metavar='filepath',
        default=argparse.SUPPRESS,
        help='Field information file for fields to be processed [default: "/imdtk/config/jwst-fields"]'
    )

    parser.add_argument(
        '-of', '--output-format', dest='output_format', metavar='format',
        default='db',
        choices=[ "db", "csv", "json", "sql"],
        help='Output format for processing results: "db", "csv", "json", or "sql" [default: "db"]'
    )

    parser.add_argument(
        '-p', '--processor', dest='processor_type', metavar='processor-type',
        default='jwst',
        help='Name of processor to use [default: "jwst"]'
    )

    parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true',
        default=False,
        help='Print informational messages during processing [default: non-verbose mode].'
    )

    parser.add_argument(
        '--version', action='version', version="%(prog)s version {}".format(VERSION),
        help='Show version information and exit.'
    )

    parser.add_argument(
        dest='image_paths', nargs="+", metavar='image',
        help='FITS image files and/or directories containing FITS images'
    )

    # actually parse the arguments from the command line
    args = vars(parser.parse_args(argv))

    # if an external aliases filepath is given, check that it exists and is readable
    check_filepath(args.get('alias_file'), 'aliases') or sys.exit(10)

    # if an external database config filepath is given, check that it exists and is readable
    check_filepath(args.get('db_config_file'), 'database configuration') or sys.exit(11)

    # if an external fields information filepath is given, check that it exists and is readable
    check_filepath(args.get('fields_file'), 'fields info') or sys.exit(12)

    # if debugging, set verbose and echo input arguments
    if (args.get('debug')):
        args['verbose'] = True              # if debug turn on verbose too
        print("(cli.main): args={}".format(args))

    # filter the given input paths for validity, removing invalid paths
    path_list = validate_path_strings(args.get('image_paths'), FITS_EXTENTS)
    if (not path_list):
        print("At least one existing, readable image file or image directory must be given. Exiting...", file=sys.stderr)
        sys.exit(21)
    else:
        args['image_paths'] = path_list

    # figure out which processor will be used on the input files (initially, only jwst implemented):
    which_processor = args.get('processor_type', 'jwst')
    if (which_processor == 'jwst'):
        processor = JwstProcessor(args)
    else:
        print("Processor type 'jwst' is currently the only processor type available. Exiting...", file=sys.stderr)
        sys.exit(22)

    # process the given, validated FITS files and directories
    proc_count = 0
    for apath in path_list:
        if (os.path.isdir(apath)):          # if it is a directory
            if (args.get('verbose')):
                log.info("(cli.main): Processing FITS files in '{}'".format(apath))
            proc_count += process_dirs(processor, apath)

        else:                               # else assume it is a file
            if (args.get('verbose')):
                log.info("(cli.main): Processing FITS file '{}'".format(apath))
            proc_count += processor.process_a_file(apath)

    # do any necessary post-processing cleanup tasks
    processor.cleanup()

    if (args.get('verbose')):
        log.info("(cli.main): Processed {} FITS files.".format(proc_count))
        print("(cli.main): Processed {} FITS files.".format(proc_count))



if __name__ == "__main__":
    main()
