# Tests of MetadataFields information manager mixin class.
#   Written by: Tom Hicks. 5/7/2020.
#   Last Modified: Update tests for no output directory argument.
#
import os
import pytest

from astropy.io import fits
from astropy import wcs

from imdtk.core.information_outputter import InformationOutputter
from imdtk.core.field_info import FieldInfo
from imdtk.core.fields_info import FieldsInfo


class TestInformationOutputter(object):

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

    # test_infout = InformationOutputter(nodebug_args)

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
        'image_paths': [ '/images/m13.fits' ],
        'metadata_table_name': 'sia.jwst'  # pass JWST-specific table name
    }

    debug_infout = InformationOutputter(debug_args)


    def test_cleanup (self):
        cleanup_infout = InformationOutputter(self.debug_args)
        cleanup_infout.cleanup()


    def test_ctor_db_no_db_config (self):
        db_args = self.debug_args.copy()
        db_args['output_format'] = 'db'     # change output format
        with pytest.raises(RuntimeError) as rterr:
            db_infout = InformationOutputter(db_args)


    def test_ctor_db_no_db_url (self):
        db_args = self.debug_args.copy()
        db_args['output_format'] = 'db'     # change output format
        db_args['db_config'] = { 'DB_HOST': 'localhost', 'DB_PORT': 5432, 'NO_DB_URL': True }
        with pytest.raises(RuntimeError) as rterr:
            db_infout = InformationOutputter(db_args)



    def test_file_info_to_string_non_sql (self):
        db_args = self.debug_args.copy()
        db_args['output_format'] = 'json'   # change output format
        json_infout = InformationOutputter(db_args)
        json = json_infout.file_info_to_string('fname', 0, '/fpath') # args not used



    def test_make_data_line_csv (self):
        db_args = self.debug_args.copy()
        db_args['output_format'] = 'csv'    # change output format
        csv_infout = InformationOutputter(db_args)
        csv = csv_infout.make_data_line(FieldsInfo())
        print(csv)
        assert csv == ''                    # LATER: implement test when method implemented


    def test_make_data_line_json (self):
        db_args = self.debug_args.copy()
        db_args['output_format'] = 'json'   # change output format
        json_infout = InformationOutputter(db_args)
        json = json_infout.make_data_line(FieldsInfo())
        print(json)
        assert json == '[]'                 # LATER: implement test when method implemented



    def test_make_file_info (self):
        # Also tests file_info_to_string
        flds_info = FieldsInfo({
            'access_estsize': FieldInfo({'obsCoreKey': 'access_estsize',
                                         'datatype': 'integer'}, value=459876),
            'file_path': FieldInfo({'obsCoreKey': 'file_path',
                                    'datatype': 'string'}, value='/astro/images/TARG1.fits'),
            'file_name': FieldInfo({'hdrKey': 'file_name',
                                    'datatype': 'string'}, value='TARG1.fits')
        })
        fylinfo = self.debug_infout.make_file_info(flds_info)
        print(fylinfo)
        assert fylinfo is not None
        assert '-- ' in fylinfo
        assert 'TARG1.fits' in fylinfo
        assert '/astro/images/TARG1.fits' in fylinfo
        assert '459876' in fylinfo



    def test_make_sql_for_db (self):
        flds_info = FieldsInfo({
            'access_estsize': FieldInfo({'obsCoreKey': 'access_estsize',
                                         'datatype': 'integer'}, value=459876),
            'file_path': FieldInfo({'obsCoreKey': 'file_path',
                                    'datatype': 'string'}, value='/astro/images/TARG1.fits'),
            'file_name': FieldInfo({'hdrKey': 'file_name',
                                    'datatype': 'string'}, value='TARG1.fits')
        })
        (template, values) = self.debug_infout.make_sql_for_db(flds_info)
        print(template, values)
        assert template is not None
        assert values is not None
        assert len(values) == 3



    def test_output_image_info (self):
        # Also tests make_file_info and make_data_line
        flds_info = FieldsInfo({
            'access_estsize': FieldInfo({'obsCoreKey': 'access_estsize',
                                         'datatype': 'integer'}, value=459876),
            'file_path': FieldInfo({'obsCoreKey': 'file_path',
                                    'datatype': 'string'}, value='/astro/images/TARG1.fits'),
            'file_name': FieldInfo({'obsCoreKey': 'file_name',
                                    'datatype': 'string'}, value='TARG1.fits'),
            's_ra': FieldInfo({'obsCoreKey': 's_ra', 'datatype': 'double'}, value=45.9876),
            's_dec': FieldInfo({'obsCoreKey': 's_dec', 'datatype': 'double'}, value=128.1234),
            'target_name': FieldInfo({'obsCoreKey': 'target_name',
                                      'datatype': 'string'}, value='TARG1'),
        })
        self.debug_infout.output_image_info(flds_info)
        assert True



    def test_to_CSV (self):
        csv = self.debug_infout.to_CSV(FieldsInfo())
        print(csv)
        assert csv == ''                    # LATER: implement test when method implemented


    def test_to_JSON (self):
        json = self.debug_infout.to_JSON(FieldsInfo())
        print(json)
        assert json == '[]'                 # LATER: implement test when method implemented


    def test_to_SQL (self):
        flds_info = FieldsInfo({
            's_ra': FieldInfo({'obsCoreKey': 's_ra', 'datatype': 'double'}, value=45.9876),
            's_dec': FieldInfo({'obsCoreKey': 's_dec', 'datatype': 'double'}, value=128.1234),
            'target_name': FieldInfo({'hdrKey': 'target_name', 'datatype': 'string'}, value='TARG1'),
        })
        sql = self.debug_infout.to_SQL(flds_info)
        print(sql)
        assert sql is not None
        assert sql.strip() != ''
        assert 'insert into sia.jwst' in sql
        assert 'values' in sql
        assert 's_ra' in sql
        assert 's_dec' in sql
        assert 'target_name' in sql
        assert '45.9876' in sql
        assert '128.1234' in sql
        assert 'TARG1' in sql
