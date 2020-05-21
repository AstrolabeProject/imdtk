# Tests of JWST-specific image metadata processing module.
#   Written by: Tom Hicks. 4/7/2020.
#   Last Modified: Add tests for calc_spatial_resolution.
#
import os
import pytest

from imdtk.core.jwst_processor import JwstProcessor
from imdtk.core.field_info import FieldInfo
from imdtk.core.fields_info import FieldsInfo


class TestJwstProcessor(object):

    m13_file = '/imdtk/tests/resources/m13.fits'
    bad_fits_file = '/imdtk/tests/resources/NOT_FITS_FILE.fits'

    nodebug_args = {
        'alias_file': None,
        'collection': None,
        'debug': False,
        'db_config_file': None,
        'fields_file': None,
        'output_format': 'sql',
        'processor_type': 'jwst',
        'verbose': False,
        'image_paths': [ '/images' ]
    }
    processor = JwstProcessor(nodebug_args)

    # debug_args = {                          # LATER: USE IN TESTS?
    #     'alias_file': None,
    #     'collection': None,
    #     'debug': True,
    #     'db_config_file': None,
    #     'fields_file': None,
    #     'output_format': 'sql',
    #     'processor_type': 'jwst',
    #     'verbose': True,
    #     'image_paths': [ '/images/m13.fits' ]
    # }
    # debproc = JwstProcessor(debug_args)     # LATER: USE IN TESTS?


    def test_ctor (self):
        proc = JwstProcessor(self.nodebug_args)


    def test_cleanup (self):
        self.processor.cleanup()
        assert True



    def test_calc_spatial_resolution_no_filter (self):
        flds_info = FieldsInfo({
            'filter': FieldInfo({'obsCoreKey': 'filter', 'datatype': 'string'}),
            's_resolution': FieldInfo({'obsCoreKey': 's_resolution', 'datatype': 'float'})
        })
        assert flds_info.has_value_for('s_resolution') == False
        self.processor.calc_spatial_resolution(flds_info)
        assert flds_info.has_value_for('s_resolution') == False


    def test_calc_spatial_resolution_bad_filter (self):
        flds_info = FieldsInfo({
            'filter': FieldInfo({'obsCoreKey': 'filter', 'datatype': 'string'}, value='BADVALUE'),
            's_resolution': FieldInfo({'obsCoreKey': 's_resolution', 'datatype': 'float'})
        })
        assert flds_info.has_value_for('s_resolution') == False
        self.processor.calc_spatial_resolution(flds_info)
        assert flds_info.has_value_for('s_resolution') == False


    def test_calc_spatial_resolution (self):
        flds_info = FieldsInfo({
            'filter': FieldInfo({'obsCoreKey': 'filter', 'datatype': 'string'}, value='F070W'),
            's_resolution': FieldInfo({'obsCoreKey': 's_resolution', 'datatype': 'float'})
        })
        assert flds_info.has_value_for('s_resolution') == False
        self.processor.calc_spatial_resolution(flds_info)
        assert flds_info.has_value_for('s_resolution') == True
        assert flds_info.get_value_for('s_resolution') == 0.030


    def test_calc_spatial_resolution (self):
        flds_info = FieldsInfo({
            'filter': FieldInfo({'obsCoreKey': 'filter', 'datatype': 'string'}, value='F444W'),
            's_resolution': FieldInfo({'obsCoreKey': 's_resolution', 'datatype': 'float'})
        })
        assert flds_info.has_value_for('s_resolution') == False
        self.processor.calc_spatial_resolution(flds_info)
        assert flds_info.has_value_for('s_resolution') == True
        assert flds_info.get_value_for('s_resolution') == 0.145



    def test_bad_fits_file (self):
        test_args = {
            'alias_file': None,
            'collection': None,
            'debug': True,
            'db_config_file': None,
            'fields_file': None,
            'output_format': 'sql',
            'processor_type': 'jwst',
            'verbose': True,
            'image_paths': [ self.bad_fits_file ]
        }
        proc = JwstProcessor(test_args)
        ret = proc.process_a_file(self.bad_fits_file)
        assert ret == 0
