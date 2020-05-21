# Tests of the FITS specific utilities module.
#   Written by: Tom Hicks. 4/7/2020.
#   Last Modified: Add a test for lookup_pixtype.
#
import imdtk.core.fits_utils as utils

import os
import pytest

from astropy import wcs
from astropy.io import fits


class TestFitsUtils(object):

    m13_file = '/imdtk/tests/resources/m13.fits'

    def test_get_header_fields_default(self):
        hdrs = {}
        with fits.open(self.m13_file) as hdus:
            hdrs = utils.get_header_fields(hdus)

        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 19              # really 25 but duplicate cards are elided
        assert 'CTYPE1' in hdrs
        assert 'COMMENT' in hdrs


    def test_get_header_fields_indexed(self):
        hdrs = {}
        with fits.open(self.m13_file) as hdus:
            hdrs = utils.get_header_fields(hdus, 0)

        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 19              # really 25 but duplicate cards are elided
        assert 'CTYPE1' in hdrs
        assert 'COMMENT' in hdrs


    def test_get_header_fields_badindex(self):
        hdrs = {}
        with fits.open(self.m13_file) as hdus:
            hdrs = utils.get_header_fields(hdus, 1) # no HDU at index 1
        assert hdrs is None



    def test_get_image_corners(self):
        corners = None
        with fits.open(self.m13_file) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
            corners = utils.get_image_corners(wcs_info)
        print(corners)
        assert len(corners) == 4
        for idx, c in enumerate(corners):
            assert len(corners[idx]) == 2



    def test_get_image_scale(self):
        scale = None
        with fits.open(self.m13_file) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
            scale = utils.get_image_scale(wcs_info)
        print(scale)
        assert len(scale) > 0
        assert len(scale) == 2
        assert scale[0] > 0



    def test_is_fits_file(self):
        assert utils.is_fits_file('m13.fits') == True
        assert utils.is_fits_file('m13.fits.gz') == True
        assert utils.is_fits_file('/usr/dummy/m13.fits') == True
        assert utils.is_fits_file('/usr/dummy/m13.fits.gz') == True

        assert utils.is_fits_file('m13') == False
        assert utils.is_fits_file('m13-fits') == False
        assert utils.is_fits_file('m13.gz') == False
        assert utils.is_fits_file('/usr/dummy/m13') == False
        assert utils.is_fits_file('/usr/dummy/m13-fits') == False
        assert utils.is_fits_file('/usr/dummy/m13.gz') == False


    def test_is_fits_filename(self):
        assert utils.is_fits_filename('m13.fits') == True
        assert utils.is_fits_filename('m13.fits.gz') == True
        assert utils.is_fits_filename('/usr/dummy/m13.fits') == True
        assert utils.is_fits_filename('/usr/dummy/m13.fits.gz') == True

        assert utils.is_fits_filename('m13') == False
        assert utils.is_fits_filename('m13.gz') == False
        assert utils.is_fits_filename('m13-fits') == False
        assert utils.is_fits_filename('/usr/dummy/m13') == False
        assert utils.is_fits_filename('/usr/dummy/m13-fits') == False
        assert utils.is_fits_filename('/usr/dummy/m13.gz') == False



    def test_get_WCS_default(self):
        wcs = None
        with fits.open(self.m13_file) as hdus:
            wcs = utils.get_WCS(hdus)
        assert wcs is not None


    def test_get_WCS_indexed(self):
        wcs = None
        with fits.open(self.m13_file) as hdus:
            wcs = utils.get_WCS(hdus, 0)
        assert wcs is not None


    def test_get_WCS_badindex(self):
        wcs = None
        with fits.open(self.m13_file) as hdus:
            wcs = utils.get_WCS(hdus, 1)   # no HDU at index 1
        assert wcs is None



    def test_metadata_keys(self):
        assert utils.get_metadata_keys({}) is None
        assert utils.get_metadata_keys({'keymissing': True}) is None
        assert utils.get_metadata_keys({'keyfile': None}) is None

        mdkeys = utils.get_metadata_keys({'keyfile': '/imdtk/tests/resources/empty.txt'})
        assert len(mdkeys) == 0

        mdkeys = utils.get_metadata_keys({'keyfile': '/imdtk/tests/resources/mdkeys.txt'})
        assert len(mdkeys) == 13

        with pytest.raises(FileNotFoundError):
            utils.get_metadata_keys({'keyfile': 'bad_filename'})


    def test_lookup_pixtype(self):
        assert utils.lookup_pixtype(0) == 'UNKNOWN'
        assert utils.lookup_pixtype('0') == 'UNKNOWN'
        assert utils.lookup_pixtype(1) == 'UNKNOWN'
        assert utils.lookup_pixtype('1') == 'UNKNOWN'
        assert utils.lookup_pixtype(-1) == 'UNKNOWN'
        assert utils.lookup_pixtype('-1') == 'UNKNOWN'
        assert utils.lookup_pixtype(100, 'NOT_FOUND') == 'NOT_FOUND'
        assert utils.lookup_pixtype('100', 'NOT_FOUND') == 'NOT_FOUND'
        assert utils.lookup_pixtype('BAD', 'BAD') == 'BAD'

        assert utils.lookup_pixtype(8) == 'byte'
        assert utils.lookup_pixtype('8') == 'byte'
        assert utils.lookup_pixtype(16) == 'short'
        assert utils.lookup_pixtype('16') == 'short'
        assert utils.lookup_pixtype(32) == 'int'
        assert utils.lookup_pixtype('32') == 'int'
        assert utils.lookup_pixtype(64) == 'long'
        assert utils.lookup_pixtype('64') == 'long'
        assert utils.lookup_pixtype(-32) == 'float'
        assert utils.lookup_pixtype('-32') == 'float'
        assert utils.lookup_pixtype(-64) == 'double'
        assert utils.lookup_pixtype('-64') == 'double'
