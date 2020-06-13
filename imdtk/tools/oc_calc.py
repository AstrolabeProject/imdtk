#
# Class to calculate values for the ObsCore fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/11/2020.
#   Last Modified: Rename this as task.
#
import os, sys
import json
import logging as log

from astropy.io import fits

from config.settings import IMAGE_FETCH_PREFIX, IMAGES_DIR
from imdtk.tools.i_tool import IImdTask, STDIN_NAME, STDOUT_NAME
import imdtk.core.fits_utils as fits_utils


class ObsCoreCalcTask (IImdTask):
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
        """ Constructor for class which calculates values for ObsCore fields in a metadata structure. """

        # Display name of this tool
        self.TOOL_NAME = args.get('TOOL_NAME') or 'obscore_calc'

        # Configuration parameters given to this class.
        self.args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = args.get('debug', False)

        # Path to a readable FITS image file from which to extract metadata.
        self._fits_file = args.get('fits_file')


    #
    # Concrete methods implementing ITask abstract methods
    #

    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for this instance. """
        if (self._DEBUG):
            print("({}.cleanup)".format(self.TOOL_NAME), file=sys.stderr)


    def process_and_output (self):
        """ Perform the main work of the tool and output the results in the selected format. """
        metadata = self.process()
        if (metadata):
            self.output_results(metadata)


    def process (self):
        """
        Perform the main work of the tool and return the results as a Python structure.
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
                fname = metadata.get('file_info').get('file_name')
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


    #
    # Non-interface and/or Task-specific Methods
    #

    def calculate_results (self, wcs_info, metadata):
        """
        Try to produce a value for each of the fields desired in the results.
        Values are extracted, calculated, or defaulted from existing metadata.
        Return a dictionary of fields and values for all fields for which
        a value was able to be produced.
        """
        calculations = dict()               # structure for calculated results

        # calculate some initial values from the FITS file WCS information
        self.calc_scale(wcs_info, calculations)
        self.calc_corners(wcs_info, calculations)

        # copy any FITS header fields that were aliased to desired result fields
        self.copy_aliased(metadata, calculations)

        # calculate any values which require special casing
        self.calc_special_case_fields(wcs_info, metadata, calculations)

        # try to produce a value for each desired field
        self.calc_field_values(wcs_info, metadata, calculations)

        return calculations


    def calc_corners (self, wcs_info, calculations):
        """
        Calculate the corner points and spatial limits for the current image,
        given the FITS file WCS information.

        The calculated corners and limits are stored in the given calculations dictionary.
        """
        corners = fits_utils.get_image_corners(wcs_info)
        if (len(corners) == 4):
            self.set_corner_field(calculations, 'im_ra1', 'im_dec1', corners[0]) # LowerLeft
            self.set_corner_field(calculations, 'im_ra2', 'im_dec2', corners[1]) # UpperLeft
            self.set_corner_field(calculations, 'im_ra3', 'im_dec3', corners[2]) # UpperRight
            self.set_corner_field(calculations, 'im_ra4', 'im_dec4', corners[3]) # LowerRight

        # now use the corners to calculate the min/max spatial limits of the image
        self.calc_spatial_limits(corners, calculations)


    def calc_scale (self, wcs_info, calculations):
        """
        Calculate the scale for the current image using the given
        given the FITS file WCS information.

        Since only the first scale value is used, this method assumes square pixels.

        The units of the scale are the same as the units of cdelt,
        crval, and cd for the celestial WCS and can be obtained by inquiring the
        value of cunit property of the input WCS object.

        The calculated scale is stored in the given calculations dictionary.
        """
        scale = fits_utils.get_image_scale(wcs_info)
        if (len(scale) > 0):
            calculations['im_scale'] = scale[0]


    def calc_field_values (self, wcs_info, metadata, calculations):
        """
        For all desired fields, compute (or recompute) a value for each field.
        Values are extracted, calculated, or defaulted from existing metadata.
        If a value is produced for a field, store the field and its value into
        the given calculations structure.
        """
        desired = metadata.get('fields_info').keys()  # make list of desired fields
        for fieldname in desired:
            self.calc_field_value(fieldname, wcs_info, metadata, calculations)
            if (fieldname not in calculations): # if field still has no value
                self.set_default(fieldname, metadata, calculations)


    def calc_field_value (self, field_name, wcs_info, metadata, calculations):
        """
        Provide the opportunity to calculate (or recalculate) a value for the named field.
        """
        if (field_name in ['s_ra', 's_dec']):
            self.calc_wcs_coordinates(wcs_info, calculations)

        elif (field_name in ['im_naxis1', 'im_naxis2']):
            if (calculations.get('s_xel1') is not None):
                calculations['im_naxis1'] = calculations.get('s_xel1')
            if (calculations.get('s_xel2') is not None):
                calculations['im_naxis2'] = calculations.get('s_xel2')

        elif (field_name == 's_resolution'):
            self.calc_spatial_resolution(calculations,
                                         filter_resolutions=self.JWST_FILTER_RESOLUTIONS)

        elif (field_name == 'im_pixtype'):
            self.calc_pixtype(metadata, calculations)

        elif (field_name == 'access_url'):
            # create URL to fetch the file from the server
            file_path = metadata.get('file_info').get('file_path')
            if (file_path is not None):
                image_path = "{0}{1}{2}".format(IMAGE_FETCH_PREFIX, IMAGES_DIR, file_path)
                calculations['access_url'] = image_path

        elif (field_name == 'instrument_name'):
            # (re)create instrument name from NIRCam + MODULE value
            module = calculations.get('nircam_module')
            inst_name = "NIRCam-{}".format(module) if (module is not None) else "NIRCam"
            calculations['instrument_name'] = inst_name

        elif (field_name == 'target_name'):
            filename = metadata.get('file_info').get('file_name')
            if (filename is not None):
                if (filename.lower().startswith("goods_s")):
                    calculations['target_name'] = "goods_south"
                elif (filename.lower().startswith("goods_n")):
                    calculations['target_name'] = "goods_north"
                else:
                    calculations['target_name'] = "UNKNOWN"


    def calc_pixtype (self, metadata, calculations):
        """
        Calculate the value string for the ObsCore im_pixeltype field based on the value
        of the FITS BITPIX keyword.
        """
        bitpix = metadata.get('headers').get('BITPIX')
        if (bitpix):
            calculations['im_pixtype'] = fits_utils.lookup_pixtype(bitpix)


    def calc_spatial_limits (self, corners, calculations):
        """
        Calculate the min/max of the RA and DEC axes from the given list of four
        image corners, each of which is a list of RA, DEC.
        """
        ras = list(map(lambda c: c[0], corners))
        decs = list(map(lambda c: c[1], corners))

        calculations['spat_lolimit1'] = min(ras)
        calculations['spat_hilimit1'] = max(ras)
        calculations['spat_lolimit2'] = min(decs)
        calculations['spat_hilimit2'] = max(decs)


    def calc_spatial_resolution (self, calculations, filter_resolutions=None):
        """
        Use the filter value to determine the spatial resolution based on a NIRCam
        filter-resolution table.
        """
        filt = calculations.get('filter')   # may not have filter field
        if (filt and filter_resolutions):   # may not know filter resolutions
            resolution = filter_resolutions.get(filt)
            if (resolution):
                calculations['s_resolution'] = resolution


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


    def calc_wcs_coordinates (self, wcs_info, calculations):
        """
        Extract the WCS coordinates for the reference pixel of the current image file.
        Sets both s_ra and s_dec fields simultaneously when either field is processed.
        This method assumes that neither s_ra nor s_dec fields have a value yet and it will
        overwrite current values for both s_ra and s_dec if that assumption is not valid.
        """
        if (('s_ra' in calculations) and ('s_dec' in calculations)): # avoid repetition
            return                          # exit out now

        crval = list(wcs_info.wcs.crval)
        ctype = list(wcs_info.wcs.ctype)

        if ((len(crval) > 1) and (len(ctype) > 1)):
            if (ctype[0].startswith('RA')):      # if CRVAL1 has the RA value
                calculations['s_ra']  = crval[0] # put CRVAL1 value into s_ra
                calculations['s_dec'] = crval[1] # put CRVAL2 value into s_dec
            elif (ctype[0].startswith('DEC')):   # else if CRVAL1 has the DEC value
                calculations['s_dec'] = crval[0] # put CRVAL1 value into s_dec
                calculations['s_ra']  = crval[1] # put CRVAL2 value into s_ra
            else:
                errMsg = "({}.calc_wcs_coords): Unable to assign RA/DEC axes from ctype={}".format(self.TOOL_NAME, ctype)
                log.error(errMsg)
                raise RuntimeError(errMsg)


    def copy_aliased (self, metadata, calculations):
        """ Copy all aliased fields to the calculations structure. """
        calculations.update(metadata.get('aliased'))


    def set_corner_field (self, calculations, ra_field_key, dec_field_key, corner):
        """
        Store the given corner coordinates [RA, DEC] into fields of the calculations
        dictionary, keyed by the given RA field keyword and DEC field keyword, respectively.
        """
        if (len(corner) > 1):               # each corner is a list of RA, DEC
            calculations[ra_field_key] = corner[0]
            calculations[dec_field_key] = corner[1]


    def set_default (self, fieldname, metadata, calculations):
        """
        Lookup the default value for the given field name and, if found, store the
        field and default value in the calculations structure.
        """
        default = metadata.get('defaults').get(fieldname)
        if (default is not None):
            calculations[fieldname] = default
