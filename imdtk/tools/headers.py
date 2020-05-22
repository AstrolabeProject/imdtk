#
# Methods for extracting header information from FITS files.
#   Written by: Tom Hicks. 5/21/2020.
#   Last Modified: Initial creation.
#

import imdtk.core.fits_utils as fits_utils


# Keys to be ignored when reading FITS file header.
# The empty key string is important: it removes any non-Key/Value lines.
FITS_IGNORE_KEYS = [ 'COMMENT', 'HISTORY', '' ]


def filter_header_fields (header_fields, ignore=FITS_IGNORE_KEYS):
    """
    Remove any entries whose keys are in the ignore list from the given header fields dictionary.
    If not given, the ignore list defaults to the value of the FITS_IGNORE_KEYS variable.
    """
    if (ignore is None):
        ignore = FITS_IGNORE_KEYS
    for key in ignore:
        header_fields.pop(key, None)        # remove keyed entry: ignore key errors



def get_header_fields (hdus_list, which_hdu=0, ignore=None):
    """
    Return a dictionary of keys and values for the cards in the selected HDU
    (default: the first HDU) or None, if the given HDU index is out of range or
    if unable to read the FITS file headers.
    """
    # make a map of all FITS headers and value strings
    header_fields = fits_utils.get_header_fields(hdus_list, which_hdu)
    if (header_fields is None):             # if unable to read the FITS file headers
        return None                         # exit out now

    # destructively remove any header fields with keys in the ignore list
    filter_header_fields(header_fields, ignore)

    return header_fields                    # return the remaining header fields
