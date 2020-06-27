#
# Class to sink incoming data to a CSV file.
#   Written by: Tom Hicks. 6/26/2020.
#   Last Modified: Initial creation.
#
import os
import sys
import configparser
import csv
import logging as log

import imdtk.core.misc_utils as misc_utils
import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import IImdTask, STDOUT_NAME

# Default file extension for pickle output files
CSV_EXTENSION = 'csv'                       # Note: no dot in extension


class CSVSink (IImdTask):
    """ Class to sink incoming data to a CSV file. """

    # List of column names to skip when outputting column values.
    skipColumnList = [ 'file_size' ]


    def __init__(self, args):
        """
        Constructor for class to sink incoming data to a CSV file.
        """
        super().__init__(args)


    #
    # Methods overriding ITask interface methods
    #

    def output_results (self, metadata):
        """
        Output a selected subset of the given metadata in CSV format.
        """
        if (self._DEBUG):
            print("({}.output_results): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # select and/or filter the data for output
        outdata, fieldnames = self.select_data_for_output(metadata)

        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')

        if (genfile):                   # if generating the output filename/path
            file_info = md_utils.get_file_info(metadata)
            fname = file_info.get('file_name') if file_info else "NO_FILENAME"
            outfile = self.gen_output_file_path(fname, CSV_EXTENSION, self.TOOL_NAME)
            self.output_CSV(outdata, fieldnames, outfile)
        elif (outfile is not None):     # else if using the given filepath
            self.output_CSV(outdata, fieldnames, outfile)
        else:                           # else using standard output
            self.output_CSV(outdata, fieldnames)

        if (self._VERBOSE):
            out_dest = outfile if (outfile) else STDOUT_NAME
            print("({}): Results output to '{}'".format(self.TOOL_NAME, out_dest), file=sys.stderr)


    #
    # Non-interface and/or task-specific Methods
    #

    def output_CSV (self, datadict, fieldnames, file_path=None):
        """
        Convert the given data structure to CSV and write it to the given file path,
        standard output, or standard error.
        """
        if ((file_path is None) or (file_path == sys.stdout)): # if writing to standard output
            writer = csv.DictWriter(sys.stdout, fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(datadict)
            # sys.stdout.write('\n')          # REMOVE LATER? may not be needed

        else:                               # else file path was given
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(datadict)
                # csvfile.write('\n')         # REMOVE LATER? may not be needed


    def select_data_for_output (self, metadata):
        """
        Select a subset of data, from the given metadata, for output.
        Returns a tuple of:
          - a singleton list containing the the dictionary of selected data and
          - a list of field names (keys in the returned dictionary) to be output
        """
        selected = md_utils.get_calculated(metadata).copy()
        misc_utils.remove_entries(selected, ignore=self.skipColumnList)
        fieldnames = list(selected.keys())  # TODO: reorder the list with filepath first LATER
        # return a tuple of the created data dictionary and list of fieldnames (keys)
        return ([selected], fieldnames)