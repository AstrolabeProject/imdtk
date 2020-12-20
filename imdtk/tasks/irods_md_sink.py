#
# Class to sink incoming metadata to an iRods file.
#   Written by: Tom Hicks. 11/30/2020.
#   Last Modified: Check that some metadata target path is specified.
#
import sys

from irods.exception import CollectionDoesNotExist, DataObjectDoesNotExist, NoResultFound

import imdtk.exceptions as errors
import imdtk.tasks.metadata_utils as md_utils
from imdtk.core.misc_utils import remove_entries
from imdtk.tasks.i_task import STDOUT_NAME, IImdTask


class IRodsMetadataSink (IImdTask):
    """ Class to sink incoming image metadata to an iRods file. """

    # List of metadata field names to skip when sinking metadata
    DEFAULT_SKIP_LIST = [ 'file_name', 'file_path', 'file_size', 'access_url', 'obs_publisher_did' ]


    def __init__(self, args, fits_irods_helper):
        """
        Constructor for class to sink incoming image metadata to an iRods file.
        """
        super().__init__(args)
        self.irods = fits_irods_helper      # IRodsHelper instance
        self.skip_list = args.get('skip_list', self.DEFAULT_SKIP_LIST)


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

        # get the iRods file path argument of the file to be annotated
        imd_path = self.args.get('irods_md_file',
                                 self.args.get('irods_fits_file'))  # default is iRods input file

        if ((imd_path is None) or (not imd_path.strip())):
            errMsg = "A full iRods path to an annotatable iRods file must be specified."
            raise errors.ProcessingError(errMsg)

        # check the iRods metadata target file path for validity
        try:
            self.irods.getf(imd_path, absolute=True)

        except (CollectionDoesNotExist, DataObjectDoesNotExist, NoResultFound):
            errMsg = "Unable to find iRods metadata attachment file at '{}'.".format(imd_path)
            raise errors.ProcessingError(errMsg)

        # select and/or filter the metadata for output
        selected = self.select_data_for_output(metadata)

        # decide whether we are storing metadata in iRods or just outputting it
        output_only = self.args.get('output_only')
        if (not output_only):               # if storing metadata to iRods
            self.store_results(imd_path, selected)

        else:                               # else just outputting metadata
            oodata = dict()
            oodata['file_info'] = md_utils.get_file_info(metadata)
            oodata['to_sink'] = selected
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
        remove_entries(selected, ignore=self.skip_list)
        return selected                     # return selected dataset


    def store_results (self, imd_path, selected):
        """
        Attach the output data dictionary to the iRods file at the specified path.
        """
        if (self._DEBUG):
            print("({}.store_results): imd_path={}, metadata={}".format(self.TOOL_NAME, imd_path, selected), file=sys.stderr)

        try:
            # try to store the selected metadata onto the iRods file node
            self.irods.put_metaf(imd_path, selected, absolute=True)

        except Exception as ex:
            errMsg = "Unable to write metadata to the iRods file at '{}'. Exception: {}".format(imd_path, ex)
            raise errors.ProcessingError(errMsg)

        if (self._VERBOSE):
            print("({}): Metadata attached to iRods file '{}'".format(self.TOOL_NAME, imd_path), file=sys.stderr)
