# Tests for the ObsCore Calculation utilities module.
#   Written by: Tom Hicks. 7/16/2020.
#   Last Modified: Update tests of calc_wcs_coordinates. Fix: rename some missed tests.
#
import pytest
from pytest import approx

from astropy import wcs
from astropy.io import fits

import imdtk.exceptions as errors
import imdtk.tasks.oc_calc_utils as utils
from tests import TEST_DIR


class TestOcCalcUtils(object):

    # empty_tstfyl  = "{}/resources/empty.txt".format(TEST_DIR)
    # mdkeys_tstfyl = "{}/resources/mdkeys.txt".format(TEST_DIR)
    table_tstfyl = "{}/resources/small_table.fits".format(TEST_DIR)
    m13_tstfyl   = "{}/resources/m13.fits".format(TEST_DIR)

    m13_meta = { 'headers': { 'CRVAL1': '250.4226', 'CRVAL2': '36.4602' }}

    filt_res = {
        'X': 1, 'YY': 2, 'ZZZ': 4
    }


    def test_calc_access_estsize_no_fileinfo(self):
        md = dict()
        calcs = dict()
        utils.calc_access_estsize(md, calcs)
        print(calcs)
        assert len(calcs) == 2
        assert calcs.get('access_estsize') == 0
        assert calcs.get('file_size') == 0


    def test_calc_access_estsize(self):
        md = { 'file_info': { 'file_name': 'nonesuch', 'file_size': 4242 }}
        calcs = dict()
        utils.calc_access_estsize(md, calcs)
        print(calcs)
        assert len(calcs) == 2
        assert calcs.get('access_estsize') == 4  # file_size in kB
        assert calcs.get('file_size') == 4242


    def test_calc_access_estsize_bigfile(self):
        md = { 'file_info': { 'file_name': 'nonesuch', 'file_size': 2666568960 }}
        calcs = dict()
        utils.calc_access_estsize(md, calcs)
        print(calcs)
        assert len(calcs) == 2
        assert calcs.get('access_estsize') == 2666569  # file_size in kB
        assert calcs.get('file_size') == 2666568960



    def test_calc_corners(self):
        # also tests calc_spatial_limits and set_corner_field
        calcs = dict()
        with fits.open(self.m13_tstfyl) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
            utils.calc_corners(wcs_info, calcs)
        print(calcs)
        assert len(calcs) == 12             # 8 corner coords (ra/dec) + 4 spatial limits (hi/lo)



    def test_calc_scale(self):
        calcs = dict()
        scale = None
        with fits.open(self.m13_tstfyl) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
            utils.calc_scale(wcs_info, calcs)
        print(calcs)
        assert len(calcs) == 1
        assert calcs.get('im_scale') == approx(0.0002777)


    def test_calc_scale_default(self):
        calcs = dict()
        scale = None
        with fits.open(self.table_tstfyl) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
            utils.calc_scale(wcs_info, calcs)
        print(calcs)
        assert len(calcs) == 1
        assert calcs.get('im_scale') == 1.0  # default if cannot be calculated



    def test_calc_pixtype_byte(self):
        md = { 'headers': { 'BITPIX': 8 }}
        calcs = dict()
        utils.calc_pixtype(md, calcs)
        print(calcs)
        assert len(calcs) == 1
        assert calcs.get('im_pixtype') == 'byte'


    def test_calc_pixtype_byte_str(self):
        md = { 'headers': { 'BITPIX': '8' }}
        calcs = dict()
        utils.calc_pixtype(md, calcs)
        print(calcs)
        assert len(calcs) == 1
        assert calcs.get('im_pixtype') == 'byte'


    def test_calc_pixtype_long(self):
        md = { 'headers': { 'BITPIX': 64 }}
        calcs = dict()
        utils.calc_pixtype(md, calcs)
        print(calcs)
        assert len(calcs) == 1
        assert calcs.get('im_pixtype') == 'long'


    def test_calc_pixtype_long_str(self):
        md = { 'headers': { 'BITPIX': '64' }}
        calcs = dict()
        utils.calc_pixtype(md, calcs)
        print(calcs)
        assert len(calcs) == 1
        assert calcs.get('im_pixtype') == 'long'


    def test_calc_pixtype_double(self):
        md = { 'headers': { 'BITPIX': -64 }}
        calcs = dict()
        utils.calc_pixtype(md, calcs)
        print(calcs)
        assert len(calcs) == 1
        assert calcs.get('im_pixtype') == 'double'


    def test_calc_pixtype_double_str(self):
        md = { 'headers': { 'BITPIX': '-64' }}
        calcs = dict()
        utils.calc_pixtype(md, calcs)
        print(calcs)
        assert len(calcs) == 1
        assert calcs.get('im_pixtype') == 'double'


    def test_calc_pixtype_badpixval(self):
        md = { 'headers': { 'BITPIX': 2 }}
        calcs = dict()
        utils.calc_pixtype(md, calcs)
        print(calcs)
        assert len(calcs) == 1
        assert calcs.get('im_pixtype') == 'UNKNOWN'

    def test_calc_pixtype_nobitpix(self):
        md = { 'headers': { 'NAXIS': 2 }}
        calcs = dict()
        utils.calc_pixtype(md, calcs)
        print(calcs)
        assert len(calcs) == 0
        assert calcs.get('im_pixtype') == None


    def test_calc_spatial_limits_simple(self):
        md = dict()
        corners = [[1.0, 11.0], [2.0, 22.0], [3.0, 33.0], [4.0, 44.0]]
        utils.calc_spatial_limits(corners, md)
        print(md)
        assert len(md) != 0
        assert md.get('spat_lolimit1') == 1.0
        assert md.get('spat_hilimit1') == 4.0
        assert md.get('spat_lolimit2') == 11.0
        assert md.get('spat_hilimit2') == 44.0



    def test_calc_spatial_limits(self):
        md = dict()
        corners = [ [ 53.1916633,  -27.843909],
                    [ 53.21085965, -27.81002265],
                    [ 53.12374317, -27.77138606],
                    [ 53.10452648, -27.80526036] ]
        utils.calc_spatial_limits(corners, md)
        print(md)
        assert len(md) != 0
        assert md.get('spat_lolimit1') == 53.10452648
        assert md.get('spat_hilimit1') == 53.21085965
        assert md.get('spat_lolimit2') == -27.843909
        assert md.get('spat_hilimit2') == -27.77138606



    def test_calc_spatial_resolution_no_filter(self):
        calcs = dict()
        utils.calc_spatial_resolution(calcs)
        assert len(calcs) == 0
        assert calcs.get('s_resolution') is None


    def test_calc_spatial_resolution_no_resolutions(self):
        calcs = { 'filter': 'F070W' }
        utils.calc_spatial_resolution(calcs)
        assert len(calcs) == 1
        assert calcs.get('s_resolution') is None


    def test_calc_spatial_resolution_bad_filter(self):
        calcs = { 'filter': 'F070W' }
        utils.calc_spatial_resolution(calcs, self.filt_res)
        assert len(calcs) == 1
        assert calcs.get('s_resolution') is None


    def test_calc_spatial_resolution(self):
        calcs = { 'filter': 'ZZZ' }
        utils.calc_spatial_resolution(calcs, self.filt_res)
        assert len(calcs) == 2
        assert calcs.get('s_resolution') is not None
        assert calcs.get('s_resolution') == 4



    def test_calc_wcs_coords(self):
        calcs = dict()
        with fits.open(self.m13_tstfyl) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
        utils.calc_wcs_coordinates(wcs_info, self.m13_meta, calcs)
        print(calcs)
        assert len(calcs) == 2
        assert 's_ra' in calcs
        assert 's_dec' in calcs
        assert calcs.get('s_ra') == 250.4226
        assert calcs.get('s_dec') == 36.4602


    def test_calc_wcs_coords_rev(self):
        calcs = dict()
        with fits.open(self.m13_tstfyl) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
        wcs_info.wcs.ctype = [ 'DEC', 'RA' ]    # reverse axes order
        utils.calc_wcs_coordinates(wcs_info, self.m13_meta, calcs)
        print(calcs)
        assert len(calcs) == 2
        assert 's_ra' in calcs
        assert 's_dec' in calcs
        assert calcs.get('s_ra') == 36.4602     # fake switch for this test
        assert calcs.get('s_dec') == 250.4226   # fake switch for this test


    def test_calc_wcs_coords_abort(self):
        calcs = { 's_ra': 140.2, 's_dec': 14.004 }
        with fits.open(self.m13_tstfyl) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
            utils.calc_wcs_coordinates(wcs_info, self.m13_meta, calcs)
        assert len(calcs) == 2
        assert 's_ra' in calcs
        assert 's_dec' in calcs


    def test_calc_wcs_coords_badmd(self):
        calcs = dict()
        with fits.open(self.m13_tstfyl) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
        md = { 'headers': { 'NOCRVAL1': None, 'NOCRVAL2': None }}
        utils.calc_wcs_coordinates(wcs_info, md, calcs)
        assert len(calcs) == 0
        assert 's_ra' not in calcs
        assert 's_dec' not in calcs


    def test_calc_wcs_coords_badaxes(self):
        calcs = dict()
        with fits.open(self.m13_tstfyl) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
        wcs_info.wcs.ctype = [ 'BAD', 'AXES' ]    # bad values for axes
        with pytest.raises(errors.ProcessingError):
            utils.calc_wcs_coordinates(wcs_info, self.m13_meta, calcs)
        assert len(calcs) == 0
        assert 's_ra' not in calcs
        assert 's_dec' not in calcs



    def test_copy_aliased(self):
        md = {
            "aliased": {
                "im_naxes": 2,
                "s_xel2": 4305,
                "gmt_date": "2019-12-14T21:10:36.490",
                "equinox": 2000.0
            }
        }
        calcs = dict()
        utils.copy_aliased(md, calcs)
        print(calcs)
        assert len(calcs) == 4
        assert 'im_naxes' in calcs
        assert 's_xel2' in calcs
        assert 'gmt_date' in calcs
        assert 'equinox' in calcs



    def test_copy_file_info(self):
        md = { 'file_info': { 'file_name': 'nonesuch', 'file_size': 4242 }}
        calcs = dict()
        utils.copy_file_info(md, calcs)
        print(calcs)
        assert len(calcs) == 2
        assert 'file_name' in calcs
        assert 'file_size' in calcs



    def test_set_default(self):
        defaults = { 'key1': 1, 'key2': 'value2', 'key3': 88.0088 }
        calcs = dict()
        utils.set_default('key2', defaults, calcs)
        print(calcs)
        assert len(calcs) == 1
        assert 'key2' in calcs


    def test_set_default_nodefaults(self):
        defaults = dict()
        calcs = dict()
        utils.set_default('key1', defaults, calcs)
        print(calcs)
        assert len(calcs) == 0
        assert 'key1' not in calcs


    def test_set_default_badkey(self):
        defaults = { 'key1': 1, 'key2': 'value2', 'key3': 88.0088 }
        calcs = dict()
        utils.set_default('KEY99', defaults, calcs)
        print(calcs)
        assert len(calcs) == 0
        assert 'key1' not in calcs
        assert 'key2' not in calcs
        assert 'key3' not in calcs
        assert 'KEY99' not in calcs
