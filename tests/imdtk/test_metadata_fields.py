# Tests of MetadataFields information manager mixin class.
#   Written by: Tom Hicks. 5/4/2020.
#   Last Modified: Add tests for minimal datetime string conversion.
#
import os
import pytest

from astropy.io import fits
from astropy.time import Time
from astropy import wcs

from imdtk.core.jwst_processor import JwstProcessor
from imdtk.core.field_info import FieldInfo
from imdtk.core.fields_info import FieldsInfo


class TestMetadataFields(object):

    m13_file = '/imdtk/tests/resources/m13.fits'

    nodebug_args = {
        'alias_file': None,
        'collection': None,
        'debug': False,
        'db_config_file': None,
        'fields_file': None,
        'output_format': 'sql',
        'processor_type': 'jwst',
        'verbose': False,
        'image_paths': [ '/images' ],
        'metadata_table_name': 'sia.jwst'  # pass JWST-specific table name
    }

    test_collection = 'TEST_COLLECTION'

    debug_args = {
        'alias_file': None,
        'collection': test_collection,
        'debug': True,
        'db_config_file': None,
        'fields_file': None,
        'output_format': 'sql',
        'processor_type': 'jwst',
        'verbose': True,
        'image_paths': [ '/images/m13.fits' ]
    }

    debug_proc = JwstProcessor(debug_args)


    def test_add_file_information_noflds (self):
        proc = JwstProcessor(self.nodebug_args)
        flds_info = FieldsInfo()
        proc.add_file_information(self.m13_file, flds_info)
        print(flds_info)
        assert len(flds_info) == 0
        assert 'file_name' not in flds_info
        assert 'file_path' not in flds_info
        assert 'access_estsize' not in flds_info


    def test_add_file_information (self):
        flds_info = FieldsInfo({
            'file_name': FieldInfo(),
            'file_path': FieldInfo(),
            'access_estsize': FieldInfo()
        })
        proc = JwstProcessor(self.nodebug_args)
        proc.add_file_information(self.m13_file, flds_info)
        print(flds_info)
        assert len(flds_info) > 0
        assert 'file_name' in flds_info
        assert 'file_path' in flds_info
        assert 'access_estsize' in flds_info
        assert flds_info.get_value_for('file_name') == 'm13.fits'
        assert flds_info.get_value_for('file_path') == self.m13_file
        assert flds_info.get_value_for('access_estsize') == 184320



    def test_add_default_value_for_a_field (self):
        fld_info = FieldInfo({'default': '3.0', 'datatype': 'float'})
        self.debug_proc.add_default_value_for_a_field(fld_info)
        print(fld_info)
        assert len(fld_info) == 3
        assert 'default' in fld_info
        assert 'datatype' in fld_info
        assert fld_info.has_value() == True


    def test_add_default_value_for_a_field_nodefault (self):
        fld_info = FieldInfo({'datatype': 'float'})
        self.debug_proc.add_default_value_for_a_field(fld_info)
        print(fld_info)
        assert len(fld_info) == 1
        assert 'datatype' in fld_info
        assert 'default' not in fld_info
        assert fld_info.has_value() == False


    def test_add_default_value_for_a_nodatatype (self):
        fld_info = FieldInfo({'default': '3.0'})
        self.debug_proc.add_default_value_for_a_field(fld_info)
        print(fld_info)
        assert len(fld_info) == 1
        assert 'default' in fld_info
        assert 'datatype' not in fld_info
        assert fld_info.has_value() == False


    def test_add_default_value_for_a_field_noreplace (self):
        fld_info = FieldInfo({'default': '-2', 'datatype': 'integer'}, value=0)
        self.debug_proc.add_default_value_for_a_field(fld_info)
        print(fld_info)
        assert len(fld_info) == 3
        assert 'default' in fld_info
        assert 'datatype' in fld_info
        assert fld_info.get_value() == 0


    def test_add_default_value_for_a_field_typeerror (self):
        fld_info = FieldInfo({'default': '3.0i', 'datatype': 'complex'}) # bad datatype
        self.debug_proc.add_default_value_for_a_field(fld_info)
        print(fld_info)
        assert len(fld_info) == 2
        assert 'default' in fld_info
        assert 'datatype' in fld_info
        assert fld_info.get_value() is None


    def test_add_default_value_for_a_field_valueerror (self):
        fld_info = FieldInfo({'default': '-3.1459', 'datatype': 'integer'}) # bad value for datatype
        self.debug_proc.add_default_value_for_a_field(fld_info)
        print(fld_info)
        assert len(fld_info) == 2
        assert 'default' in fld_info
        assert 'datatype' in fld_info
        assert fld_info.get_value() is None



    def test_calc_spatial_limits_simple (self):
        corners = [[1.0, 11.0], [2.0, 22.0], [3.0, 33.0], [4.0, 44.0]]
        flds_info = FieldsInfo({
            'spat_lolimit1': FieldInfo({}),
            'spat_hilimit1': FieldInfo({}),
            'spat_lolimit2': FieldInfo({}),
            'spat_hilimit2': FieldInfo({})
        })
        self.debug_proc.calc_spatial_limits(corners, flds_info)
        print(flds_info)
        assert len(flds_info) != 0
        assert flds_info.get_value_for('spat_lolimit1') == 1.0
        assert flds_info.get_value_for('spat_hilimit1') == 4.0
        assert flds_info.get_value_for('spat_lolimit2') == 11.0
        assert flds_info.get_value_for('spat_hilimit2') == 44.0


    def test_calc_spatial_limits (self):
        corners = [ [ 53.1916633,  -27.843909],
                    [ 53.21085965, -27.81002265],
                    [ 53.12374317, -27.77138606],
                    [ 53.10452648, -27.80526036] ]
        flds_info = FieldsInfo({
            'spat_lolimit1': FieldInfo({}),
            'spat_hilimit1': FieldInfo({}),
            'spat_lolimit2': FieldInfo({}),
            'spat_hilimit2': FieldInfo({})
        })
        self.debug_proc.calc_spatial_limits(corners, flds_info)
        print(flds_info)
        assert len(flds_info) != 0
        assert flds_info.get_value_for('spat_lolimit1') == 53.10452648
        assert flds_info.get_value_for('spat_hilimit1') == 53.21085965
        assert flds_info.get_value_for('spat_lolimit2') == -27.843909
        assert flds_info.get_value_for('spat_hilimit2') == -27.77138606



    def test_calc_wcs_coords (self):
        with fits.open(self.m13_file) as ff_hdus_list:
            wcs_info = wcs.WCS(ff_hdus_list[0].header)
        fi_ra = FieldInfo({'obsCoreKey': 's_ra', 'datatype': 'double'})
        fi_dec = FieldInfo({'obsCoreKey': 's_dec', 'datatype': 'double'})
        flds_info = FieldsInfo({'s_ra': fi_ra, 's_dec': fi_dec})
        self.debug_proc.calc_wcs_coords(wcs_info, None, flds_info)
        print(flds_info)
        assert flds_info.has_value_for('s_ra') == True
        assert flds_info.has_value_for('s_dec') == True
        assert flds_info.get_value_for('s_ra') == 250.4226
        assert flds_info.get_value_for('s_dec') == 36.4602


    def test_calc_wcs_coords_rev (self):
        with fits.open(self.m13_file) as ff_hdus_list:
            wcs_info = wcs.WCS(ff_hdus_list[0].header)
        wcs_info.wcs.ctype = [ 'DEC', 'RA' ]    # reverse axes order

        fi_ra = FieldInfo({'obsCoreKey': 's_ra', 'datatype': 'double'})
        fi_dec = FieldInfo({'obsCoreKey': 's_dec', 'datatype': 'double'})
        flds_info = FieldsInfo({'s_ra': fi_ra, 's_dec': fi_dec})

        self.debug_proc.calc_wcs_coords(wcs_info, None, flds_info)
        print(flds_info)
        assert flds_info.has_value_for('s_ra') == True
        assert flds_info.has_value_for('s_dec') == True
        assert flds_info.get_value_for('s_ra') == 36.4602    # fake switch for this test
        assert flds_info.get_value_for('s_dec') == 250.4226  # fake switch for this test


    def test_calc_wcs_coords_fail (self):
        with fits.open(self.m13_file) as ff_hdus_list:
            wcs_info = wcs.WCS(ff_hdus_list[0].header)
        wcs_info.wcs.ctype = [ 'BAD', 'AXES' ]    # bad values for axes

        fi_ra = FieldInfo({'obsCoreKey': 's_ra', 'datatype': 'double'})
        fi_dec = FieldInfo({'obsCoreKey': 's_dec', 'datatype': 'double'})
        flds_info = FieldsInfo({'s_ra': fi_ra, 's_dec': fi_dec})

        self.debug_proc.calc_wcs_coords(wcs_info, None, flds_info)
        print(flds_info)
        assert flds_info.has_value_for('s_ra') == False
        assert flds_info.has_value_for('s_dec') == False


    def test_compute_values_for_fields_texptime (self):
        # special case test for JWST special case: set missing t_exptime
        fi_dummy = FieldInfo({'hdrKey': 'target_name', 'hdrValueStr': '11',
                              'datatype': 'integer'}, value=11)
        fi_exptime = FieldInfo({'hdrKey': 't_exptime', 'hdrValueStr': '0.0',
                                'datatype': 'float'}, value=0.0)
        flds_info = FieldsInfo({'t_exptime': fi_exptime, 'dummy': fi_dummy})
        self.debug_proc.compute_values_for_fields(None, None, flds_info) # args not needed yet
        assert flds_info.get_value_for('t_exptime') == 1347.0


    def test_compute_values_for_fields_collection (self):
        self._args = self.debug_args
        fi_coll = FieldInfo({'hdrKey': 'obs_collection', 'hdrValueStr': 'NONE',
                             'datatype': 'string'})
        flds_info = FieldsInfo({'obs_collection': fi_coll})
        self.debug_proc.compute_values_for_fields(None, None, flds_info) # args not needed yet
        assert flds_info.get_value_for('obs_collection') == self.test_collection



    def test_compute_value_for_a_field_hasvalue (self):
        fi_hasval = FieldInfo({'obsCoreKey': 'HASVALUE', 'datatype': 'integer'}, value=11)
        self.debug_proc.compute_value_for_a_field(fi_hasval, None, None, None) # args not needed yet
        assert fi_hasval.get_value() == 11  # should be unchanged


    def test_compute_value_for_a_field_targetname_s (self):
        test_fname = 'goods_s_test_file.fits'
        fi_tname = FieldInfo({'obsCoreKey': 'target_name', 'datatype': 'string'})
        fi_fname = FieldInfo({'obsCoreKey': 'file_name', 'datatype': 'string'}, value=test_fname)
        flds_info = FieldsInfo({'file_name': fi_fname})
        self.debug_proc.compute_value_for_a_field(fi_tname, None, None, flds_info)
        assert fi_tname.get_value() == 'goods_south'


    def test_compute_value_for_a_field_targetname_n (self):
        test_fname = 'GOODS_N_TEST_FILE.fits'
        fi_tname = FieldInfo({'obsCoreKey': 'target_name', 'datatype': 'string'})
        fi_fname = FieldInfo({'obsCoreKey': 'file_name', 'datatype': 'string'}, value=test_fname)
        flds_info = FieldsInfo({'file_name': fi_fname})
        self.debug_proc.compute_value_for_a_field(fi_tname, None, None, flds_info)
        assert fi_tname.get_value() == 'goods_north'


    def test_compute_value_for_a_field_targetname_unk (self):
        test_fname = 'NOT_GOODS_TEST_FILE.fits'
        fi_tname = FieldInfo({'obsCoreKey': 'target_name', 'datatype': 'string'})
        fi_fname = FieldInfo({'obsCoreKey': 'file_name', 'datatype': 'string'}, value=test_fname)
        flds_info = FieldsInfo({'file_name': fi_fname})
        self.debug_proc.compute_value_for_a_field(fi_tname, None, None, flds_info)
        assert fi_tname.get_value() == 'UNKNOWN'



    def test_convert_a_header_value (self):
        fld_info = FieldInfo({'hdrKey': 'TESTKEY', 'hdrValueStr': '3.0',
                              'datatype': 'float'})
        self.debug_proc.convert_a_header_value(fld_info)
        print(fld_info)
        assert len(fld_info) == 4
        assert 'hdrKey' in fld_info
        assert 'hdrValueStr' in fld_info
        assert 'datatype' in fld_info
        assert fld_info.get_value() is not None


    def test_convert_a_header_value_novalue (self):
        fld_info = FieldInfo({'hdrKey': 'TESTKEY', 'datatype': 'float'})
        self.debug_proc.convert_a_header_value(fld_info)
        print(fld_info)
        assert len(fld_info) == 2
        assert 'hdrKey' in fld_info
        assert 'datatype' in fld_info
        assert 'hdrValueStr' not in fld_info
        assert fld_info.get_value() is None


    def test_convert_a_header_value_nodatatype (self):
        fld_info = FieldInfo({'hdrKey': 'TESTKEY', 'hdrValueStr': '3.0'})
        self.debug_proc.convert_a_header_value(fld_info)
        print(fld_info)
        assert len(fld_info) == 2
        assert 'hdrKey' in fld_info
        assert 'hdrValueStr' in fld_info
        assert 'datatype' not in fld_info
        assert fld_info.get_value() is None


    def test_convert_a_header_value_replaced (self):
        fld_info = FieldInfo({'hdrKey': 'TESTKEY', 'hdrValueStr': '-2',
                              'datatype': 'integer'}, value=0)
        self.debug_proc.convert_a_header_value(fld_info)
        print(fld_info)
        assert len(fld_info) == 4
        assert 'hdrKey' in fld_info
        assert 'hdrValueStr' in fld_info
        assert 'datatype' in fld_info
        assert fld_info.get_value() == -2


    def test_convert_a_header_value_typeerror (self):
        fld_info = FieldInfo({'hdrKey': 'TESTKEY', 'hdrValueStr': '3.0i',
                              'datatype': 'complex'}) # bad datatype
        self.debug_proc.convert_a_header_value(fld_info)
        print(fld_info)
        assert len(fld_info) == 3
        assert 'hdrKey' in fld_info
        assert 'hdrValueStr' in fld_info
        assert 'datatype' in fld_info
        assert fld_info.get_value() is None


    def test_convert_a_header_value_valueerror (self):
        fld_info = FieldInfo({'hdrKey': 'TESTKEY', 'hdrValueStr': '-3.1459',
                              'datatype': 'integer'}) # bad value for this datatype
        self.debug_proc.convert_a_header_value(fld_info)
        print(fld_info)
        assert len(fld_info) == 3
        assert 'hdrValueStr' in fld_info
        assert 'datatype' in fld_info
        assert fld_info.get_value() is None



    def test_string_to_value_none (self):
        assert self.debug_proc.string_to_value('3', None) is None
        assert self.debug_proc.string_to_value('value', None) is None
        assert self.debug_proc.string_to_value(None, 'integer') is None
        assert self.debug_proc.string_to_value(None, 'string') is None
        assert self.debug_proc.string_to_value('', 'integer') is None
        assert self.debug_proc.string_to_value('', 'date') is None


    def test_string_to_value_bad_type (self):
        with pytest.raises(TypeError) as verr:
            self.debug_proc.string_to_value('1', 'badtype')
        with pytest.raises(TypeError) as verr:
            self.debug_proc.string_to_value('2', 'int')
        with pytest.raises(TypeError) as verr:
            self.debug_proc.string_to_value('2', 'INT')


    def test_string_to_value_bad_value (self):
        with pytest.raises(ValueError) as verr:
            self.debug_proc.string_to_value('1.0', 'integer')
        with pytest.raises(ValueError) as verr:
            self.debug_proc.string_to_value('double', 'double')
        with pytest.raises(ValueError) as verr:
            self.debug_proc.string_to_value('float', 'float')

    def test_string_to_value (self):
        assert self.debug_proc.string_to_value('3', 'integer') == 3
        assert self.debug_proc.string_to_value('0', 'integer') == 0
        assert self.debug_proc.string_to_value('-3', 'integer') == -3
        assert self.debug_proc.string_to_value('1.0', 'float') == 1.0
        assert self.debug_proc.string_to_value('0', 'float') == 0
        assert self.debug_proc.string_to_value('-1.0', 'float') == -1.0
        assert self.debug_proc.string_to_value('0', 'string') == '0'
        assert self.debug_proc.string_to_value(7, 'string') == '7'
        assert self.debug_proc.string_to_value(7.7, 'string') == '7.7'

        # TODO: update following tests when implemented LATER:
        tyme = self.debug_proc.string_to_value('2001-01-02 03:04:05.678', 'date')
        print(tyme)
        assert tyme is not None
        assert isinstance(tyme, Time)

        tyme = self.debug_proc.string_to_value('2002-01-02', 'date')
        print(tyme)
        assert tyme is not None
        assert isinstance(tyme, Time)

        with pytest.raises(ValueError) as verr:
            badt = self.debug_proc.string_to_value('2003', 'date') # year alone not enough



        ######### EXTRA CODE for later ##########

        # with fits.open(self.m13_file) as ff_hdus_list:
        #     wcs_info = wcs.WCS(ff_hdus_list[0].header)
