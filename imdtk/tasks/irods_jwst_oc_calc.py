#
# Class to calculate values for the ObsCore fields in an iRods FITS-file-derived metadata structure.
#   Written by: Tom Hicks. 11/20/20.
#   Last Modified: Fix: tool name reference.
#
import sys

import imdtk.exceptions as errors
import imdtk.core.fits_irods_helper as firh
import imdtk.core.fits_utils as fits_utils
from imdtk.tasks.jwst_oc_calc import JWST_ObsCoreCalcTask


class IRods_JWST_ObsCoreCalcTask (JWST_ObsCoreCalcTask):
    """
    Class which calculates values for ObsCore fields from metadata
    derived from an iRods-resident FITS file.
    """

    def __init__(self, args):
        """
        Constructor for class which calculates values for ObsCore fields from metadata
        derived from an iRods-resident FITS file.
        """
        super().__init__(args)
        self.irods = None                   # holder for IRodsHelper instance


    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for the task instance. """
        if (self.irods):
            self.irods.cleanup()
        super().cleanup


    #
    # Concrete method overriding JWST_ObsCoreCalcTask method
    #

    def process (self, metadata):
        """
        Perform the main work of the task and return the results as a Python data structure.
        This method overrides JWST_ObsCoreCalcTask method to use iRods file access.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # use the specified HDU of the FITS file to compute the WCS information
        which_hdu = self.args.get('which_hdu', 0)

        # get the iRods file path argument of the file to be opened
        irff_path = self.args.get('irods_fits_file')

        # the specified FITS file must have a valid FITS extension
        if (not fits_utils.is_fits_filename(irff_path)):
            errMsg = "A readable, valid FITS image filepath must be specified.".format(irff_path)
            raise errors.ProcessingError(errMsg)

        try:
            # get an instance of the iRods accessor class
            self.irods = firh.FitsIRodsHelper(self.args)

            # get the FITS file at the specified path
            irff = self.irods.getf(irff_path, absolute=True)

            # sanity check on the given FITS file
            if (irff.size < firh.FITS_BLOCK_SIZE):
                errMsg = "File is too small to be a valid FITS file: '{}'".format(irff_path)
                raise errors.UnsupportedTypeError(errMsg)

            if (self._DEBUG):
                print("({}): Reading iRods FITS file '{}'.".format(self.TOOL_NAME, irff_path), file=sys.stderr)

            # try to get the specified header and read WCS info from it
            header = self.irods.get_header(irff, which_hdu)
            if (header):
                wcs_info = self.irods.get_WCS(header)
            else:                           # unable to read the specified header
                errMsg = "Unable to find or read HDU {} of FITS file '{}'.".format(which_hdu, irff_path)
                raise errors.ProcessingError(errMsg)

        except DataObjectDoesNotExist as dodne:
            errMsg = "Unable to find the specified iRods FITS file '{}'.".format(irff_path)
            raise errors.ProcessingError(errMsg)

        except OSError as oserr:
            errMsg = "Unable to read WCS info from iRods FITS file '{}': {}.".format(irff_path, oserr)
            raise errors.ProcessingError(errMsg)

        # check that we got the WCS information from the file
        if (wcs_info is None):
            errMsg = "No WCS info found in iRods FITS file '{}'.".format(irff_path)
            raise errors.ProcessingError(errMsg)

        # try to produce values for each of the desired result fields
        calculated = self.calculate_results(wcs_info, metadata)
        metadata['calculated'] = calculated  # add calculations to metadata

        return metadata                      # return the results of processing
