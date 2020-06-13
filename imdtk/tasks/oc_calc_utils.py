#
# Utilities to calculate values for the ObsCore fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/11/2020.
#   Last Modified: Convert class to module of utilities.
#
import os, sys
import logging as log

import imdtk.core.fits_utils as fits_utils


def calc_corners (wcs_info, calculations):
    """
    Calculate the corner points and spatial limits for the current image,
    given the FITS file WCS information.

    The calculated corners and limits are stored in the given calculations dictionary.
    """
    corners = fits_utils.get_image_corners(wcs_info)
    if (len(corners) == 4):
        set_corner_field(calculations, 'im_ra1', 'im_dec1', corners[0]) # LowerLeft
        set_corner_field(calculations, 'im_ra2', 'im_dec2', corners[1]) # UpperLeft
        set_corner_field(calculations, 'im_ra3', 'im_dec3', corners[2]) # UpperRight
        set_corner_field(calculations, 'im_ra4', 'im_dec4', corners[3]) # LowerRight

    # now use the corners to calculate the min/max spatial limits of the image
    calc_spatial_limits(corners, calculations)


def calc_scale (wcs_info, calculations):
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


def calc_pixtype (metadata, calculations):
    """
    Calculate the value string for the ObsCore im_pixeltype field based on the value
    of the FITS header BITPIX keyword.
    """
    hdrs = get_headers(metadata)
    if (hdrs):
        bitpix = hdrs.get('BITPIX')
        if (bitpix):
            calculations['im_pixtype'] = fits_utils.lookup_pixtype(bitpix)


def calc_spatial_limits (corners, calculations):
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


def calc_spatial_resolution (calculations, filter_resolutions=None):
    """
    Use the filter value to determine the spatial resolution based on a NIRCam
    filter-resolution table.
    """
    filt = calculations.get('filter')       # may not have filter field
    if (filt and filter_resolutions):       # may not know filter resolutions
        resolution = filter_resolutions.get(filt)
        if (resolution):
            calculations['s_resolution'] = resolution


def calc_wcs_coordinates (wcs_info, calculations, tool_name=''):
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
            errMsg = "({}.calc_wcs_coords): Unable to assign RA/DEC axes from ctype={}".format(tool_name, ctype)
            log.error(errMsg)
            raise RuntimeError(errMsg)


def copy_aliased (metadata, calculations):
    """ Copy all aliased fields to the calculations structure. """
    aliased = get_aliased(metadata)
    if (aliased):
        calculations.update(aliased)


def get_aliased (metadata):
    """ Accessor for the aliased dictionary embedded in the given metadata structure. """
    return metadata.get('aliased')


def get_defaults (metadata):
    """ Accessor for the defaults dictionary embedded in the given metadata structure. """
    return metadata.get('defaults')


def get_fields_info (metadata):
    """ Accessor for the fields_info dictionary embedded in the given metadata structure. """
    return metadata.get('fields_info')


def get_file_info (metadata):
    """ Accessor for the file_info dictionary embedded in the given metadata structure. """
    return metadata.get('file_info')


def get_headers (metadata):
    """ Accessor for the headers dictionary embedded in the given metadata structure. """
    return metadata.get('headers')


def set_corner_field (calculations, ra_field_key, dec_field_key, corner):
    """
    Store the given corner coordinates [RA, DEC] into fields of the calculations
    dictionary, keyed by the given RA field keyword and DEC field keyword, respectively.
    """
    if (len(corner) > 1):               # each corner is a list of RA, DEC
        calculations[ra_field_key] = corner[0]
        calculations[dec_field_key] = corner[1]


def set_default (fieldname, defaults, calculations):
    """
    Lookup the default value for the given field name and, if found, store the
    field and default value in the calculations structure.
    """
    default = defaults.get(fieldname)
    if (default is not None):
        calculations[fieldname] = default
