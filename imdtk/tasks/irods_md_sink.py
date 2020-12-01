#
# Class to sink incoming metadata to an iRods file.
#   Written by: Tom Hicks. 11/30/2020.
#   Last Modified: WIP: Initial creation.
#
import sys

import imdtk.exceptions as errors
import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import STDOUT_NAME, IImdTask


class IRodsMetadataSink (IImdTask):
    """ Class to sink incoming image metadata to an iRods file. """

    def __init__(self, args, fits_irods_helper):
        """
        Constructor for class to sink incoming image metadata to an iRods file.
        """
        super().__init__(args)
        self.irods = fits_irods_helper      # IRodsHelper instance


    #
    # Methods overriding IImdTask interface methods
    #

    def output_results (self, metadata):
        """
        Store the given data into the configured database OR just output SQL
        to do so, depending on the 'output-only' flag.
        """
        if (self._DEBUG):
            print("({}.output_results): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # select and/or filter the metadata for output
        outdata = self.select_data_for_output(metadata)

        # decide whether we are storing metadata in iRods or just outputting it
        output_only = self.args.get('output_only')
        if (not output_only):               # if storing metadata to iRods
            self.store_results(metadata, outdata)

        else:                               # else just outputting metadata
            oodata = dict()
            oodata['file_info'] = md_utils.get_file_info(metadata)
            oodata['to_sink'] = outdata
            super().output_results(oodata)


    #
    # Non-interface and/or task-specific Methods
    #

    def select_data_for_output (self, metadata):
        """
        Select a subset of data, from the given metadata, for output.
        Returns a single dictionary of selected data.
        """
        calculated = md_utils.get_calculated(metadata)
        if (not calculated):
            errMsg = "The 'calculated' data, required by this program, is missing from the input."
            raise errors.ProcessingError(errMsg)

        selected = calculated.copy()
        # TODO: IMPLEMENT ignore list (see csv sink)  
        #       Should ignore file_name, file_path, file_size, access_url, obs_publisher_did
        # remove_entries(selected, ignore=self.skipColumnList)
        return selected                     # return selected dataset


    def store_results (self, metadata, outdata):
        """
        Attach the output data dictionary to the specified or default iRods file.
        """
        if (self._DEBUG):
            print("({}.store_results)".format(self.TOOL_NAME), file=sys.stderr)

        # get the iRods file path arguments of the files to be opened
        irff_path = self.args.get('irods_fits_file')
        imd_path = self.args.get('irods_md_file', irff_path)  # default is iRods input file

        # TODO: IMPLEMENT LATER  

        if (self._VERBOSE):
            print("({}): Metadata attached to '{}'".format(self.TOOL_NAME, imd_path), file=sys.stderr)
