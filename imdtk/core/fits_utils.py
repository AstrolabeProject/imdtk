#
# Module to provide FITS utility functions for Astrolabe code.
#   Written by: Tom Hicks. 1/26/2020.
#   Last Modified: Add method to dump FITS table as JSON.
#
import fnmatch
import json
from collections import OrderedDict

from astropy import wcs
from astropy.time import Time
from astropy.wcs.utils import proj_plane_pixel_scales
from numpyencoder import NumpyEncoder

from imdtk.core.file_utils import gen_file_paths, validate_file_path
from imdtk.core.misc_utils import to_JSON


# patterns for identifying FITS and gzipped FITS files
_FITS_PAT = "*.fits"
_GZFITS_PAT = "*.fits.gz"

# suffixes for identifying FITS and gzipped FITS files
FITS_EXTENTS = [ '.fits', '.fits.gz' ]

# Common keys to be ignored when reading FITS file header.
# The empty key string is important: it removes any non-Key/Value lines.
FITS_IGNORE_KEYS = [ 'COMMENT', 'HISTORY', '' ]

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


def gen_fits_file_paths (root_dir):
    """ Generator to yield all FITS files in the file tree under the given root directory. """
    for file_path in gen_file_paths(root_dir):
        if (validate_file_path(file_path, FITS_EXTENTS)):
            yield file_path


def get_column_info (hdus_list, which_hdu=1):
    """
    Return a dictionary of metadata describing the columns of the table in the
    specified HDU. Per Astropy, the returned dictionary contains arrays of metadata,
    each containing values for a particular property for each table column (e.g., name,
    format, unit, bscale, etc).
    """
    col_md = None
    try:
        if (which_hdu < len(hdus_list)):    # if HDU index is in valid range
            col_md = hdus_list[which_hdu].columns.info(output=False)
    except AttributeError:                  # probably wrong HDU was specified
        return None
    return col_md


def get_header_fields (hdus_list, which_hdu=0, ignore=FITS_IGNORE_KEYS):
    """
    Return a dictionary of keys and values for the cards in the selected HDU
    (default: 0 (the first HDU)) or None, if the given HDU index is out of range.
    The result dictionary will not contain entries for cards whose keys are
    in the given "ignore list". Note that the result dictionary will contain only the
    last value found for duplicate keys.
    """
    if (which_hdu >= len(hdus_list)):       # sanity check
        return None
    hdrs = dict()
    header = hdus_list[which_hdu].header
    filtered = [ card for card in header.items() if (card[0] not in ignore) ]
    hdrs.update(filtered)
    return hdrs


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


def is_catalog_file (ff_hdus_list, which_hdu=1):
    """ Tell whether the given FITS file is a FITS catalog or not.
        Assumes: catalog HDU must be of type BINTABLE:
    """
    return ( (len(ff_hdus_list) > which_hdu) and
             (ff_hdus_list[which_hdu].header.get('XTENSION') == 'BINTABLE') )


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


def table_to_JSON (table, **json_kwargs):
    """
    Create a JSON string from the given astropy.table.Table object.
    Written by: JHunkeler at StSci.

    :param table: astropy.table.Table
        The extra parameter, table.meta, if present, is expected to be
        a dictionary of FITS keyword/value pairs.
    :param json_kwargs: dictionary containing arguments to the json.dumps call.
    :return a JSON string
    """
    outdata = {}                            # dictionary to be dumped as JSON
    try:
        outdata['header'] = table.meta      # table metadata is optional
    except AttributeError:
        pass
    outdata['columns'] = OrderedDict((name, list(table[name])) for name in table.colnames)
    return to_JSON(outdata, cls=NumpyEncoder)
