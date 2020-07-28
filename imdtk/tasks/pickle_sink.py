#
# Class to sink incoming data to a python pickle file on disk.
#   Written by: Tom Hicks. 6/17/2020.
#   Last Modified: Remove unused import.
#
import pickle
import sys

import imdtk.exceptions as errors
import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import IImdTask, STDOUT_NAME

# Default file extension for pickle output files
PICKLE_EXTENSION = 'pickle'                 # Note: no dot in extension


class PickleSink (IImdTask):
    """ Class to sink incoming data to a python pickle file on disk. """

    def __init__(self, args):
        """
        Constructor for class to sink incoming data to a python pickle file on disk.
        """
        super().__init__(args)


    #
    # Methods overriding IImdTask interface methods
    #

    def output_results (self, metadata):
        """ Output the given metadata in the configured output format. """
        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')

        if (genfile):                       # if generating the output filename/path
            file_info = md_utils.get_file_info(metadata)
            fname = file_info.get('file_name') if file_info else "NO_FILENAME"
            outfile = self.gen_output_file_path(fname, PICKLE_EXTENSION, self.TOOL_NAME)
            self.output_pickle(metadata, outfile)
        elif (outfile is not None):         # else if using the given filepath
            self.output_pickle(metadata, outfile)
        else:                               # else trying to use standard output
            errMsg = "Pickle cannot be written to {}.".format(STDOUT_NAME)
            raise errors.ProcessingError(errMsg)

        if (self._VERBOSE):
            print("({}): Pickled data output to '{}'".format(self.TOOL_NAME, outfile), file=sys.stderr)


    #
    # Non-interface and/or task-specific Methods
    #

    def output_pickle (self, data, file_path, protocol=None):
        """ Pickle the given data and write it to the given output file. """
        if ((file_path is None) or (file_path == sys.stdout)): # if trying standard output
            return                          # exit out now
        else:                               # else file path was given
            with open(file_path, 'wb') as outfile:
                pickle.dump(data, outfile, protocol)
