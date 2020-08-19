# Tests for the FITS-specific PostgreSQL interface module.
#   Written by: Tom Hicks. 8/10/2020.
#   Last Modified: Add tests for clean_id.
#
import pytest

import imdtk.exceptions as errors
import imdtk.core.pg_gen_sql as pg_gen
import imdtk.tasks.i_sql_sink as isql
from tests import TEST_DBCONFIG_FILEPATH


class TestFitsPgSql(object):

    args = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestFitsPgSql', 'catalog_table': 'myCatalog' }

    # load DB test configuration parameters
    task = isql.ISQLSink(args)
    dbconfig = task.load_sql_db_config(TEST_DBCONFIG_FILEPATH)
    print("TestFitsPgSql:dbconfig={}".format(dbconfig))

    cat_names = [
        "ID",
        "RA",
        "DEC",
        "redshift",
        "x",
        "y",
        "a",
        "bb",
        "ccc",
        "kron_flag"
    ]
    cat_formats = [
        "A",
        "D",
        "E",
        "F",
        "I",
        "J",
        "K",
        "L",
        "X",
        "Z"
    ]

    format_codes = {
        'A': 'text',
        'D': 'double precision',
        'E': 'real',
        'F': 'real',
        'I': 'smallint',
        'J': 'integer',
        'K': 'bigint',
        'L': 'boolean',
        'X': 'bit',
        'Z': 'bytea'
    }


    def test_check_missing_parameters_noreq(self):
        miss = pg_gen.check_missing_parameters(self.dbconfig, [])
        assert miss is None


    def test_check_missing_parameters_nomiss(self):
        has_params = ['db_uri', 'db_schema_name', 'db_user']
        miss = pg_gen.check_missing_parameters(self.dbconfig, has_params)
        assert miss is None


    def test_check_missing_parameters_miss(self):
        bad_params = ['db_db', 'dba', 'bb', 'CCC']
        emsg = f'Missing required .* {bad_params}'
        with pytest.raises(errors.ProcessingError, match=emsg):
            pg_gen.check_missing_parameters(self.dbconfig, bad_params)


    def test_check_missing_parameters_mixed(self):
        mix_params = ['db_uri', 'dba', 'bb', 'db_user', 'CCC', 'db_name']
        bad_params = ['dba', 'bb', 'CCC']
        emsg = f'Missing required .* {bad_params}'
        with pytest.raises(errors.ProcessingError, match=emsg):
            pg_gen.check_missing_parameters(self.dbconfig, mix_params)



    def test_clean_id_empty(self):
        with pytest.raises(errors.ProcessingError, match='cannot be empty or None'):
            pg_gen.clean_id(None)

        with pytest.raises(errors.ProcessingError, match='cannot be empty or None'):
            pg_gen.clean_id('')

        with pytest.raises(errors.ProcessingError, match='cannot be empty or None'):
            pg_gen.clean_id('', '')


    def test_clean_id(self):
        assert pg_gen.clean_id('_') == '_'
        assert pg_gen.clean_id('a') == 'a'
        assert pg_gen.clean_id('_a_') == '_a_'
        assert pg_gen.clean_id('_ABC_') == '_ABC_'
        assert pg_gen.clean_id('abc_') == 'abc_'
        assert pg_gen.clean_id('ABCxyz') == 'ABCxyz'


    def test_clean_id_remove(self):
        assert pg_gen.clean_id('ABC xyz') == 'ABCxyz'
        assert pg_gen.clean_id('*ABC;xyz') == 'ABCxyz'
        assert pg_gen.clean_id('*ABC;xyz') == 'ABCxyz'
        assert pg_gen.clean_id('Robert;drop all tables;') == 'Robertdropalltables'


    def test_clean_id_allow(self):
        letvec = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        assert pg_gen.clean_id('ABC xyz', letvec) == ''
        assert pg_gen.clean_id('xyz; ABC', letvec) == ''
        assert pg_gen.clean_id('abc xyz', letvec) == 'abc'
        assert pg_gen.clean_id('XYZ; abc', letvec) == 'abc'
        assert pg_gen.clean_id('Robert;drop all tables;', letvec) == 'bedaabe'



    def test_fits_format_to_sql_unsup(self):
        for fcode in ['B', 'C', 'M', 'P', 'Q', 'BAD', 'CRAZY']:
            with pytest.raises(errors.ProcessingError, match='is not supported'):
                pg_gen.fits_format_to_sql(fcode)


    def test_fits_format_to_sql(self):
        for fcode in self.format_codes.keys():
            dtype = pg_gen.fits_format_to_sql(fcode)
            print(dtype)
            assert dtype == self.format_codes.get(fcode)


    def test_fits_format_to_sql_long(self):
        fcodes = ['A40', 'D3.2', 'E1.0', 'F2.1', 'I4.1', 'J12', 'K128', 'L2', 'X8', 'Z2']
        dtypes = [ pg_gen.fits_format_to_sql(fcode) for fcode in fcodes ]
        print(dtypes)
        assert dtypes == list(self.format_codes.values())



    def test_gen_column_decls_sql_empty(self):
        sql = pg_gen.gen_column_decls_sql([], [])
        print(sql)
        assert sql is not None
        assert len(sql) == 0


    def test_gen_column_decls_sql_nofmt(self):
        with pytest.raises(errors.ProcessingError, match='lists must be the same length'):
            pg_gen.gen_column_decls_sql(['NAME'], [])


    def test_gen_column_decls_sql_noname(self):
        with pytest.raises(errors.ProcessingError, match='lists must be the same length'):
            pg_gen.gen_column_decls_sql([], ['K'])


    def test_gen_column_decls_sql_unequal(self):
        with pytest.raises(errors.ProcessingError, match='lists must be the same length'):
            pg_gen.gen_column_decls_sql(['f1', 'f2', 'f3'], ['K', 'J'])


    def test_gen_column_decls_sql(self):
        sql = pg_gen.gen_column_decls_sql(self.cat_names, self.cat_formats)
        print(sql)
        assert sql is not None
        assert len(sql) == len(self.cat_names)
        assert sql[0] == 'ID text'
        assert sql[1] == 'RA double precision'
        assert sql[2] == 'DEC real'
        assert sql[5] == 'y integer'
        assert sql[8] == 'ccc bit'
        assert sql[9] == 'kron_flag bytea'


    def test_gen_search_path_sql_bad(self):
        with pytest.raises(errors.ProcessingError):
            pg_gen.gen_search_path_sql(dict())


    def test_gen_search_path_sql(self):
        schema = self.dbconfig.get('DB_SCHEMA_NAME') or 'sia'
        sql = pg_gen.gen_search_path_sql(self.dbconfig)
        print(sql)
        assert sql is not None
        assert len(sql) > 0
        assert "SET search_path TO {}".format(schema) in sql[0]
