# Tests of the FITS specific utilities module.
#   Written by: Tom Hicks. 4/7/2020.
#   Last Modified: Update/add tests for get_column_info and is_catalog_file.
#
import imdtk.core.fits_utils as utils

import os
import pytest

from astropy import wcs
from astropy.io import fits


class TestFitsUtils(object):

    m13_file = '/imdtk/tests/resources/m13.fits'
    small_table = '/imdtk/tests/resources/small_table.fits'


    def test_get_column_info(self):
        with fits.open(self.small_table) as hdus:
            col_info = utils.get_column_info(hdus)
            assert col_info is not None


    def test_get_column_info_good_hdu(self):
        with fits.open(self.small_table) as hdus:
            col_info = utils.get_column_info(hdus, which_hdu=1)
            assert col_info is not None


    def test_get_column_info_no_table(self):
        with fits.open(self.m13_file) as hdus:
            col_info = utils.get_column_info(hdus)
            assert col_info is None


    def test_get_column_info_bad_low_hdu(self):
        with fits.open(self.small_table) as hdus:
            col_info = utils.get_column_info(hdus, which_hdu=0)
            assert col_info is None


    def test_get_column_info_bad_high_hdu(self):
        with fits.open(self.small_table) as hdus:
            col_info = utils.get_column_info(hdus, which_hdu=2)
            assert col_info is None



    def test_get_header_fields_default(self):
        hdrs = None
        with fits.open(self.m13_file) as hdus:
            hdrs = utils.get_header_fields(hdus)

        print(hdrs)
        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 18              # really 25 but duplicates elided, comments removed
        assert 'CTYPE1' in hdrs
        assert 'SIMPLE' in hdrs
        assert 'COMMENT' not in hdrs        # removed by default


    def test_get_header_fields_indexed(self):
        hdrs = None
        with fits.open(self.m13_file) as hdus:
            hdrs = utils.get_header_fields(hdus, 0)

        print(hdrs)
        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 18              # really 25 but duplicates elided, comments removed
        assert 'CTYPE1' in hdrs
        assert 'SIMPLE' in hdrs
        assert 'COMMENT' not in hdrs        # removed by default


    def test_get_header_fields_badindex(self):
        hdrs = None
        with fits.open(self.m13_file) as hdus:
            hdrs = utils.get_header_fields(hdus, 1) # no HDU at index 1
        assert hdrs is None


    def test_get_header_fields_ignore_key(self):
        hdrs = None
        with fits.open(self.m13_file) as hdus:
            hdrs = utils.get_header_fields(hdus, ignore=['SIMPLE', ''])

        print(hdrs)
        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 18              # really 25 but duplicates elided
        assert 'CTYPE1' in hdrs
        assert 'SIMPLE' not in hdrs         # removed explicitly
        assert 'COMMENT' in hdrs            # should not be removed


    def test_get_header_fields_ignore_min(self):
        hdrs = None
        with fits.open(self.m13_file) as hdus:
            hdrs = utils.get_header_fields(hdus, ignore=[''])

        print(hdrs)
        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 19              # really 25 but duplicates elided
        assert 'CTYPE1' in hdrs
        assert 'SIMPLE' in hdrs
        assert 'COMMENT' in hdrs            # should not be removed


    def test_get_header_fields_ignore_empty(self):
        hdrs = None
        with fits.open(self.m13_file) as hdus:
            hdrs = utils.get_header_fields(hdus, ignore=[])

        print(hdrs)
        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 19              # really 25 but duplicates elided
        assert 'CTYPE1' in hdrs
        assert 'SIMPLE' in hdrs
        assert 'COMMENT' in hdrs            # should not be removed



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



    def test_is_catalog_file(self):
        with fits.open(self.small_table) as hdus:
            assert utils.is_catalog_file(hdus) == True


    def test_is_catalog_file_good_hdu(self):
        with fits.open(self.small_table) as hdus:
            assert utils.is_catalog_file(hdus, which_hdu=1) == True


    def test_is_catalog_file_no_cat(self):
        with fits.open(self.m13_file) as hdus:
            assert utils.is_catalog_file(hdus) == False


    def test_is_catalog_file_bad_low_hdu(self):
        with fits.open(self.small_table) as hdus:
            assert utils.is_catalog_file(hdus, which_hdu=0) == False


    def test_is_catalog_file_bad_high_hdu(self):
        with fits.open(self.small_table) as hdus:
            assert utils.is_catalog_file(hdus, which_hdu=2) == False




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
