#
# Class to extract image metadata from iRods-resident FITS image files.
#   Written by: Tom Hicks. 10/15/20.
#   Last Modified: Refactor: pass iRods helper in ctor.
#
import os
import sys

from irods.exception import DataObjectDoesNotExist

import imdtk.exceptions as errors
import imdtk.core.fits_utils as fits_utils
from imdtk.core.fits_utils import FITS_BLOCK_SIZE, FITS_IGNORE_KEYS
from imdtk.tasks.i_task import IImdTask


class IRodsFitsImageMetadataTask (IImdTask):
    """ Class to extract image metadata from iRods-resident FITS image files. """

    def __init__(self, args, fits_irods_helper):
        """
        Constructor for class to extract image metadata from iRods-resident FITS image files.
        """
        super().__init__(args)
        self.irods = fits_irods_helper      # IRodsHelper instance


    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for the task instance. """
        if (self.irods):
            self.irods.cleanup()
        super().cleanup


    #
    # Methods overriding IImdTask interface methods
    #

    def process (self, _):
        """
        Perform the main work of the task and return the results as a Python data structure.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # get the selection and filtering arguments
        which_hdu = self.args.get('which_hdu', 0)
        ignore_list = self.args.get('ignore_list') or fits_utils.FITS_IGNORE_KEYS

        # get the iRods file path argument of the file to be opened
        irff_path = self.args.get('irods_fits_file')

        try:
            # get the FITS file at the specified path
            irff = self.irods.getf(irff_path, absolute=True)

            # sanity check on the given FITS file
            if (irff.size < FITS_BLOCK_SIZE):
                errMsg = "File is too small to be a valid FITS file: '{}'".format(irff_path)
                raise errors.UnsupportedTypeError(errMsg)

            # actually read the file to get the specified header
            header = self.irods.get_header(irff, which_hdu)
            if (header):
                if (not self.irods.is_image_header(header)):
                    errMsg = "HDU {} is not an image header. Skipping FITS file '{}'.".format(which_hdu, irff_path)
                    raise errors.ProcessingError(errMsg)

                # get and save some common file information
                file_info = self.irods.get_irods_file_info(irff)

                # get additional metadata ABOUT the iRods file itself
                irods_metadata = self.irods.get_irods_metadata(irff)

                # get any content metadata attached to the file
                content_metadata = self.irods.get_content_metadata(irff)

                # now try to read the FITS header from the FITS file
                hdrs = fits_utils.get_fields_from_header(header, ignore_list)

            else:                           # unable to read the specified header
                errMsg = "Unable to read image metadata from HDU {} of FITS file '{}'.".format(which_hdu, irff_path)
                raise errors.ProcessingError(errMsg)

        except DataObjectDoesNotExist as dodne:
            errMsg = "Unable to find the specified iRods FITS file '{}'.".format(irff_path)
            raise errors.ProcessingError(errMsg)

        except OSError as oserr:
            errMsg = "Unable to read image metadata from iRods FITS file '{}': {}.".format(irff_path, oserr)
            raise errors.ProcessingError(errMsg)

        metadata = dict()                   # create overall metadata structure
        metadata['file_info'] = file_info   # add previously gathered remote file information
        metadata['irods_metadata'] = irods_metadata
        metadata['content_metadata'] = content_metadata

        if (hdrs is not None):
            metadata['headers'] = hdrs      # add the headers to the metadata
        return metadata                     # return the results of processing
