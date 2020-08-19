# Tests for the FITS-specific PostgreSQL interface module.
#   Written by: Tom Hicks. 8/10/2020.
#   Last Modified: Update for update of make table module.
#
import pytest

import imdtk.exceptions as errors
import imdtk.core.pg_make_table_sql as pgmt
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


    def test_check_dbconfig_parameters_noreq(self):
        miss = pgmt.check_dbconfig_parameters(self.dbconfig, [])
        assert miss is None


    def test_check_dbconfig_parameters_nomiss(self):
        has_params = ['db_uri', 'db_schema_name', 'db_user']
        miss = pgmt.check_dbconfig_parameters(self.dbconfig, has_params)
        assert miss is None


    def test_check_dbconfig_parameters_miss(self):
        bad_params = ['db_db', 'dba', 'bb', 'CCC']
        emsg = f'Missing required .* {bad_params}'
        with pytest.raises(errors.ProcessingError, match=emsg):
            pgmt.check_dbconfig_parameters(self.dbconfig, bad_params)


    def test_check_dbconfig_parameters_mixed(self):
        mix_params = ['db_uri', 'dba', 'bb', 'db_user', 'CCC', 'db_name']
        bad_params = ['dba', 'bb', 'CCC']
        emsg = f'Missing required .* {bad_params}'
        with pytest.raises(errors.ProcessingError, match=emsg):
            pgmt.check_dbconfig_parameters(self.dbconfig, mix_params)



    def test_fits_format_to_sql_unsup(self):
        for fcode in ['B', 'C', 'M', 'P', 'Q', 'BAD', 'CRAZY']:
            with pytest.raises(errors.ProcessingError, match='is not supported'):
                pgmt.fits_format_to_sql(fcode)


    def test_fits_format_to_sql(self):
        for fcode in self.format_codes.keys():
            dtype = pgmt.fits_format_to_sql(fcode)
            print(dtype)
            assert dtype == self.format_codes.get(fcode)


    def test_fits_format_to_sql_long(self):
        fcodes = ['A40', 'D3.2', 'E1.0', 'F2.1', 'I4.1', 'J12', 'K128', 'L2', 'X8', 'Z2']
        dtypes = [ pgmt.fits_format_to_sql(fcode) for fcode in fcodes ]
        print(dtypes)
        assert dtypes == list(self.format_codes.values())



    def test_gen_column_decls_sql_empty(self):
        sql = pgmt.gen_column_decls_sql([], [])
        print(sql)
        assert sql is not None
        assert len(sql) == 0


    def test_gen_column_decls_sql_nofmt(self):
        with pytest.raises(errors.ProcessingError, match='lists must be the same length'):
            pgmt.gen_column_decls_sql(['NAME'], [])


    def test_gen_column_decls_sql_noname(self):
        with pytest.raises(errors.ProcessingError, match='lists must be the same length'):
            pgmt.gen_column_decls_sql([], ['K'])


    def test_gen_column_decls_sql_unequal(self):
        with pytest.raises(errors.ProcessingError, match='lists must be the same length'):
            pgmt.gen_column_decls_sql(['f1', 'f2', 'f3'], ['K', 'J'])


    def test_gen_column_decls_sql(self):
        sql = pgmt.gen_column_decls_sql(self.cat_names, self.cat_formats)
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
            pgmt.gen_search_path_sql(dict())


    def test_gen_search_path_sql(self):
        schema = self.dbconfig.get('DB_SCHEMA_NAME') or 'sia'
        sql = pgmt.gen_search_path_sql(self.dbconfig)
        print(sql)
        assert sql is not None
        assert len(sql) > 0
        assert "SET search_path TO {}".format(schema) in sql[0]
