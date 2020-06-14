#
# Class to calculate values for the ObsCore fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/13/2020.
#   Last Modified: Update for abstract method reduction.
#
import os, sys
import logging as log

from astropy.io import fits

from config.settings import IMAGE_FETCH_PREFIX, IMAGES_DIR
from imdtk.tasks.i_task import STDIN_NAME, STDOUT_NAME
from imdtk.tasks.i_oc_calc import IObsCoreCalcTask
import imdtk.core.fits_utils as fits_utils
import imdtk.tasks.metadata_utils as md_utils
import imdtk.tasks.oc_calc_utils as occ_utils


class JWST_ObsCoreCalcTask (IObsCoreCalcTask):
    """ Class to calculate values for ObsCore fields in a metadata structure. """

    # Spatial resolutions for NIRCam filters, keyed by filter name.
    JWST_FILTER_RESOLUTIONS = {
        'F070W': 0.030, 'F090W': 0.034,  'F115W': 0.040,  'F140M': 0.048, 'F150W': 0.050,
        'F162M': 0.055, 'F164N': 0.056,  'F150W2': 0.046, 'F182M': 0.062, 'F187N': 0.064,
        'F200W': 0.066, 'F210M': 0.071,  'F212N': 0.072,  'F250M': 0.084, 'F277W': 0.091,
        'F300M': 0.100, 'F322W2': 0.097, 'F323N': 0.108,  'F335M': 0.111, 'F356W': 0.115,
        'F360M': 0.120, 'F405N': 0.136,  'F410M': 0.137,  'F430M': 0.145, 'F444W': 0.145,
        'F460M': 0.155, 'F466N': 0.158,  'F470N': 0.160,  'F480M': 0.162
    }


    def __init__(self, args):
        """
        Constructor for class which calculates values for ObsCore fields in a metadata structure.
        """
        super().__init__(args)

        # Display name of this task
        self.TOOL_NAME = args.get('TOOL_NAME') or 'jwst_oc_calc'

        # Configuration parameters given to this class.
        self.args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = args.get('debug', False)

        # Path to a readable FITS image file from which to extract metadata.
        self._fits_file = args.get('fits_file')


    #
    # Concrete methods implementing ITask and IObsCoreCalcTask abstract methods
    #

    def process (self):
        """
        Perform the main work of the task and return the results as a Python structure.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # process the given, already validated FITS file
        fits_file = self.args.get('fits_file')
        if (self._VERBOSE):
            print("({}): Reading FITS file '{}'".format(self.TOOL_NAME, fits_file), file=sys.stderr)

        # compute the WCS information from the specified HDU of the FITS file
        which_hdu = self.args.get('which_hdu', 0)
        with fits.open(fits_file) as hdus_list:
            wcs_info = fits_utils.get_WCS(hdus_list, which_hdu)

        if (wcs_info is None):
            errMsg = "({}.process): Unable to read WCS info from FITS file '{}'.".format(self.TOOL_NAME, fits_file)
            log.error(errMsg)
            raise RuntimeError(errMsg)

        # process the given, already validated input file
        input_file = self.args.get('input_file')
        if (self._VERBOSE):
            if (input_file is None):
                print("({}): Processing metadata from {}".format(self.TOOL_NAME, STDIN_NAME), file=sys.stderr)
            else:
                print("({}): Processing metadata file '{}'".format(self.TOOL_NAME, input_file), file=sys.stderr)

        # read metadata from the input file in the specified input format
        input_format = self.args.get('input_format') or DEFAULT_INPUT_FORMAT
        metadata = self.input_JSON(input_file, input_format, self.TOOL_NAME)

        # try to produce values for each of the desired result fields
        calculated = self.calculate_results(wcs_info, metadata)
        metadata['calculated'] = calculated # add calculations to metadata

        return metadata                     # return the results of processing


    def output_results (self, metadata):
        """ Output the given metadata in the selected format. """
        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')
        out_fmt = self.args.get('output_format') or 'json'

        if (out_fmt == 'json'):
            if (genfile):                   # if generating the output filename/path
                file_info = md_utils.get_file_info(metadata)
                fname = file_info.get('file_name') if file_info else "NO_FILENAME"
                outfile = self.gen_output_file_path(fname, out_fmt, self.TOOL_NAME)
                self.output_JSON(metadata, outfile)
            elif (outfile is not None):     # else if using the given filepath
                self.output_JSON(metadata, outfile)
            else:                           # else using standard output
                self.output_JSON(metadata)

        else:
            errMsg = "({}.process): Invalid output format '{}'.".format(self.TOOL_NAME, out_fmt)
            log.error(errMsg)
            raise ValueError(errMsg)

        if (self._VERBOSE):
            out_dest = outfile if (outfile) else STDOUT_NAME
            print("({}): Results output to '{}'".format(self.TOOL_NAME, out_dest), file=sys.stderr)


    def calc_access_url (self, metadata, calculations):
        """ Use the given metadata to create the URL to fetch the file from the server. """
        file_info = md_utils.get_file_info(metadata)
        file_path = file_info.get('file_path') if file_info else None
        if (file_path is not None):
            image_path = "{0}{1}{2}".format(IMAGE_FETCH_PREFIX, IMAGES_DIR, file_path)
            calculations['access_url'] = image_path


    def calc_instrument_name (self, metadata, calculations):
        """
        Use the given metadata to create re/create an instrument name.
        This version creates the instrument name from NIRCam + MODULE value
        """
        module = calculations.get('nircam_module')
        inst_name = "NIRCam-{}".format(module) if (module is not None) else "NIRCam"
        calculations['instrument_name'] = inst_name


    def calc_spatial_resolution (self, calculations, filter_resolutions=JWST_FILTER_RESOLUTIONS):
        """
        Use the filter value to determine the spatial resolution based on the
        default NIRCam filter-resolution table.
        """
        occ_utils.calc_spatial_resolution(calculations, filter_resolutions)


    def calc_target_name (self, metadata, calculations):
        """
        Use the given metadata to create re/create a target name.
        This version is a crude heuristic based on early JWST filenames.
        """
        file_info = md_utils.get_file_info(metadata)
        filename = file_info.get('file_name') if file_info else None
        if (filename is not None):
            if (filename.lower().startswith("goods_s")):
                calculations['target_name'] = "goods_south"
            elif (filename.lower().startswith("goods_n")):
                calculations['target_name'] = "goods_north"
            else:
                calculations['target_name'] = "UNKNOWN"


    #
    # Non-interface and/or task-specific Methods
    #

    def calc_special_case_fields (self, wcs_info, metadata, calculations):
        """ Perform special case calculations. """

        #  special case: correct the t_exptime zero value with a
        #                default of 1347.0 per Eiichi Egami 20190626.
        #
        t_exptime = calculations.get('t_exptime')
        if (t_exptime == 0.0):
            calculations['t_exptime'] = 1347.0

        # special case: if given a collection name argument, then use it.
        collection = self.args.get('collection')
        if (collection):
            calculations['obs_collection'] = collection
