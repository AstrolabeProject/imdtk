#
# Class to sink incoming metadata to an iRods file.
#   Written by: Tom Hicks. 11/30/2020.
#   Last Modified: Add capability to just remove metadata items.
#
import sys

from irods.exception import CollectionDoesNotExist, DataObjectDoesNotExist, NetworkException, NoResultFound

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
            errMsg = "Unable to find iRods file for metadata alteration at '{}'.".format(imd_path)
            raise errors.ProcessingError(errMsg)

        # extract the data to be output from the given metadata
        sink_data = self.get_data_for_output(metadata)

        # When adding/replacing metadata, skip items in the skip list,
        # otherwise do not skip any items: remove all user specified items
        remove_only = self.args.get('remove_only') or False
        if (not remove_only):
            remove_entries(sink_data, ignore=self.skip_list)

        # decide whether we are changing metadata in iRods or just outputting it
        output_only = self.args.get('output_only')
        if (not output_only):               # if storing metadata to iRods
            self.update_metadata(imd_path, sink_data, remove_only)

        else:                               # else just outputting metadata
            oodata = dict()
            oodata['file_info'] = md_utils.get_file_info(metadata)
            oodata['to_sink'] = sink_data
            super().output_results(oodata)


    #
    # Non-interface and/or task-specific Methods
    #

    def get_data_for_output (self, metadata):
        """
        Extract the data to be output from the given metadata. Currently, just returns a
        copy of the "calculated" dictionary.
        """
        calculated = md_utils.get_calculated(metadata)
        if (not calculated):
            errMsg = "The 'calculated' data, required by this program, is missing from the input."
            raise errors.ProcessingError(errMsg)

        copied = calculated.copy()
        return copied


    def update_metadata (self, imd_path, sink_data, remove_only=False):
        """
        Attach or remove the items in the given data dictionary to/from the iRods file
        at the specified path. If the remove_only flag is True, file metadata items with
        keys matching input item keys are removed from the iRods file.
        """
        if (self._DEBUG):
            print(f"({self.TOOL_NAME}.update_metadata): imd_path={imd_path}, remove_only={remove_only} metadata={sink_data}", file=sys.stderr)

        try:
            if (remove_only):
                # try to remove the specified metadata from the iRods file node
                self.irods.remove_metaf(imd_path, sink_data, absolute=True)
                action = 'removed from'
            else:
                # try to attach the given metadata to the iRods file node
                self.irods.put_metaf(imd_path, sink_data, absolute=True)
                action = 'attached to'

        except (NetworkException, Exception) as ex:
            errMsg = f"Unable to alter the metadata of the iRods file at '{imd_path}'. Exception: {ex}"
            raise errors.ProcessingError(errMsg)

        if (self._VERBOSE):
            print(f"({self.TOOL_NAME}): Metadata {action} iRods file '{imd_path}'", file=sys.stderr)
