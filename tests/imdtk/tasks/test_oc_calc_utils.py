# Tests for the ObsCore Calculation utilities module.
#   Written by: Tom Hicks. 7/16/2020.
#   Last Modified: Initial creation.
#
import pytest

import imdtk.tasks.oc_calc_utils as utils


class TestOcCalcUtils(object):

    filt_res = {
        'X': 1, 'YY': 2, 'ZZZ': 4
    }

    # def test_calc_access_estsize(self):
    #     # TODO: IMPLEMENT LATER
    #     assert False


    # def test_calc_corners(self):
    #     # TODO: IMPLEMENT LATER
    #     assert False


    # def test_calc_scale(self):
    #     # TODO: IMPLEMENT LATER
    #     assert False

    # def test_calc_pixtype(self):
    #     # TODO: IMPLEMENT LATER
    #     assert False


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



    # def test_calc_spatial_resolution(self):
    #     flds_info = FieldsInfo({
    #         'filter': FieldInfo({'obsCoreKey': 'filter', 'datatype': 'string'}, value='F444W'),
    #         's_resolution': FieldInfo({'obsCoreKey': 's_resolution', 'datatype': 'float'})
    #     })
    #     assert flds_info.has_value_for('s_resolution') == False
    #     self.processor.calc_spatial_resolution(flds_info)
    #     assert flds_info.has_value_for('s_resolution') == True
    #     assert flds_info.get_value_for('s_resolution') == 0.145


    # def test_calc_wcs_coords(self):
    #     with fits.open(self.m13_file) as ff_hdus_list:
    #         wcs_info = wcs.WCS(ff_hdus_list[0].header)
    #     fi_ra = FieldInfo({'obsCoreKey': 's_ra', 'datatype': 'double'})
    #     fi_dec = FieldInfo({'obsCoreKey': 's_dec', 'datatype': 'double'})
    #     flds_info = FieldsInfo({'s_ra': fi_ra, 's_dec': fi_dec})
    #     self.debug_proc.calc_wcs_coords(wcs_info, None, flds_info)
    #     print(flds_info)
    #     assert flds_info.has_value_for('s_ra') == True
    #     assert flds_info.has_value_for('s_dec') == True
    #     assert flds_info.get_value_for('s_ra') == 250.4226
    #     assert flds_info.get_value_for('s_dec') == 36.4602


    # def test_calc_wcs_coords_rev(self):
    #     with fits.open(self.m13_file) as ff_hdus_list:
    #         wcs_info = wcs.WCS(ff_hdus_list[0].header)
    #     wcs_info.wcs.ctype = [ 'DEC', 'RA' ]    # reverse axes order

    #     fi_ra = FieldInfo({'obsCoreKey': 's_ra', 'datatype': 'double'})
    #     fi_dec = FieldInfo({'obsCoreKey': 's_dec', 'datatype': 'double'})
    #     flds_info = FieldsInfo({'s_ra': fi_ra, 's_dec': fi_dec})

    #     self.debug_proc.calc_wcs_coords(wcs_info, None, flds_info)
    #     print(flds_info)
    #     assert flds_info.has_value_for('s_ra') == True
    #     assert flds_info.has_value_for('s_dec') == True
    #     assert flds_info.get_value_for('s_ra') == 36.4602    # fake switch for this test
    #     assert flds_info.get_value_for('s_dec') == 250.4226  # fake switch for this test


    # def test_calc_wcs_coords_fail(self):
    #     with fits.open(self.m13_file) as ff_hdus_list:
    #         wcs_info = wcs.WCS(ff_hdus_list[0].header)
    #     wcs_info.wcs.ctype = [ 'BAD', 'AXES' ]    # bad values for axes

    #     fi_ra = FieldInfo({'obsCoreKey': 's_ra', 'datatype': 'double'})
    #     fi_dec = FieldInfo({'obsCoreKey': 's_dec', 'datatype': 'double'})
    #     flds_info = FieldsInfo({'s_ra': fi_ra, 's_dec': fi_dec})

    #     self.debug_proc.calc_wcs_coords(wcs_info, None, flds_info)
    #     print(flds_info)
    #     assert flds_info.has_value_for('s_ra') == False
    #     assert flds_info.has_value_for('s_dec') == False


    # def test_copy_aliased(self):
    #     # TODO: IMPLEMENT LATER
    #     assert False

    # def test_copy_file_info(self):
    #     # TODO: IMPLEMENT LATER
    #     assert False

    # def test_set_corner_field(self):
    #     # TODO: IMPLEMENT LATER
    #     assert False

    # def test_set_default(self):
    #     # TODO: IMPLEMENT LATER
    #     assert False
