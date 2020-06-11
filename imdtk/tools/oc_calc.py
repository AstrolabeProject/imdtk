#
# Class to calculate values for the ObsCore fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/11/2020.
#   Last Modified: Add calc_corners and calc_spatial limits.
#
import os, sys
import json
import logging as log

from astropy.io import fits

import imdtk.core.fits_utils as fits_utils
from imdtk.tools.i_tool import IImdTool, STDIN_NAME, STDOUT_NAME


class ObsCoreCalcTask (IImdTool):
    """ Class to calculate values for ObsCore fields in a metadata structure. """

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
    # Concrete methods implementing ITool abstract methods
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

        # perform the various calculations and accumulate them
        calculations = dict()

        self.calc_scale(wcs_info, calculations)
        self.calc_corners(wcs_info, calculations)
        # TODO: IMPLEMENT more calculations LATER

        metadata['calculated'] = calculations # add calculations to metadata

        return metadata                 # return the results of processing


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
    # Non-interface and/or Tool-specific Methods
    #

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


    def set_corner_field (self, calculations, ra_field_key, dec_field_key, corner):
        """
        Store the given corner coordinates [RA, DEC] into fields of the calculations
        dictionary, keyed by the given RA field keyword and DEC field keyword, respectively.
        """
        if (len(corner) > 1):               # each corner is a list of RA, DEC
            calculations[ra_field_key] = corner[0]
            calculations[dec_field_key] = corner[1]
