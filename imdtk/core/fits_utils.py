#
# Module to provide FITS utility functions for Astrolabe code.
#   Written by: Tom Hicks. 1/26/2020.
#   Last Modified: Add minimal datetime string conversion.
#
import fnmatch
import os

from astropy import wcs
from astropy.time import Time
from astropy.wcs.utils import proj_plane_pixel_scales


# patterns for identifying FITS and gzipped FITS files
_FITS_PAT = "*.fits"
_GZFITS_PAT = "*.fits.gz"

# suffixes for identifying FITS and gzipped FITS files
FITS_EXTENTS = [ '.fits', '.fits.gz' ]

# MIME type for FITS files
FITS_MIME_TYPE = 'image/fits'

# FITS data type code to name translation table
PIXTYPE_TABLE = {
     8:  'byte',  16: 'short',   32:  'int',  64:  'long',  -32:  'float',  -64:  'double',
    '8': 'byte', '16': 'short', '32': 'int', '64': 'long', '-32': 'float', '-64': 'double',
}


def fits_utc_date (value_str, scale='utc'):
    """
    Return an astropy.time.Time object parsed from the given datetime string using
    the optional time scale.
    """
    # TODO: Better implementation: this will only work for well-formed, complete date strings
    #       and defaults to UTC scale.
    #   see: https://docs.astropy.org/en/stable/time/
    #   see: https://docs.astropy.org/en/stable/api/astropy.time.Time.html
    return Time(value_str)


def get_header_fields (ff_hdus_list, which_hdu=0):
    """
    Return a dictionary of keys and values for the cards in the selected HDU
    (default: the first HDU) or None, if the given HDU index is out of range.
    """
    if (which_hdu >= len(ff_hdus_list)):    # sanity check
        return None
    return dict(ff_hdus_list[which_hdu].header)


def get_image_corners (wcs):
    """
    Return the image corners as a list, given a valid WCS object, extracted from the image.
    Corners are listed clockwise from the lower left corner.
    """
    return list(wcs.calc_footprint())


def get_image_scale (wcs):
    """
    Return the image scale as a list of projection plane increments corresponding to each axis,
    calculated from the given FITS file WCS information.

    The units of the returned results are the same as the units of cdelt,
    crval, and cd for the celestial WCS and can be obtained by inquiring the
    value of cunit property of the input WCS object.
    """
    return list(proj_plane_pixel_scales(wcs))


def get_metadata_keys (args):
    """
    Return a list of metadata keys to be extracted.

    throws FileNotFoundError is given a non-existant or unreadable filepath.
    """
    keyfile = args.get("keyfile")
    if (keyfile):
        with open(keyfile, "r") as mdkeys_file:
            return mdkeys_file.read().splitlines()
    else:
        return None


def get_WCS (ff_hdus_list, which_hdu=0):
    """
    Return a World Coordinate System structure from the header in the specified HDU
    (default: the first HDU) or None, if the given HDU index is out of range.
    """
    if (which_hdu >= len(ff_hdus_list)):    # sanity check
        return None
    return wcs.WCS(ff_hdus_list[which_hdu].header)


def is_catalog_file (ff_hdus_list):
    """ Tell whether the given FITS file is a FITS catalog or not.
        Assumes: catalog is never in the first HDU and HDU must be of type BINTABLE:
    """
    return ((len(ff_hdus_list) > 1) and (ff_hdus_list[1].header.get('XTENSION') == 'BINTABLE'))


def is_fits_file (fyl):
    """ Return True if the given file is FITS file, else False. """
    return (fnmatch.fnmatch(fyl, _FITS_PAT) or fnmatch.fnmatch(fyl, _GZFITS_PAT))


def is_fits_filename (filename, extents=FITS_EXTENTS):
    """ Return True if the given filename string names a FITS file, else False. """
    return (filename.endswith(tuple(extents)))


def lookup_pixtype (bitpix, default='UNKNOWN'):
    """
    Return the pixel data type for the given FITS header code value from the BITPIX field.
    Returns default value if the code is not found upon lookup.
    """
    return PIXTYPE_TABLE.get(bitpix, default)
