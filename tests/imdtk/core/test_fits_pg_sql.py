# Tests for the FITS-specific PostgreSQL interface module.
#   Written by: Tom Hicks. 8/10/2020.
#   Last Modified: Initial creation.
#
import pytest

from config.settings import DEC_ALIASES, ID_ALIASES, RA_ALIASES
import imdtk.exceptions as errors
import imdtk.core.fits_pg_sql as fpg
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


    def test_fits_format_to_sql_unsup(self):
        for fcode in ['B', 'C', 'M', 'P', 'Q', 'BAD', 'CRAZY']:
            with pytest.raises(errors.ProcessingError, match='is not supported'):
                fpg.fits_format_to_sql(fcode)


    def test_fits_format_to_sql(self):
        for fcode in self.format_codes.keys():
            dtype = fpg.fits_format_to_sql(fcode)
            print(dtype)
            assert dtype == self.format_codes.get(fcode)


    def test_fits_format_to_sql_long(self):
        fcodes = ['A40', 'D3.2', 'E1.0', 'F2.1', 'I4.1', 'J12', 'K128', 'L2', 'X8', 'Z2']
        dtypes = [ fpg.fits_format_to_sql(fcode) for fcode in fcodes ]
        print(dtypes)
        assert dtypes == list(self.format_codes.values())



    def test_gen_column_decls_sql_empty(self):
        sql = fpg.gen_column_decls_sql([], [])
        print(sql)
        assert sql is not None
        assert len(sql) == 0


    def test_gen_column_decls_sql_nofmt(self):
        with pytest.raises(errors.ProcessingError, match='lists must be the same length'):
            fpg.gen_column_decls_sql(['NAME'], [])


    def test_gen_column_decls_sql_noname(self):
        with pytest.raises(errors.ProcessingError, match='lists must be the same length'):
            fpg.gen_column_decls_sql([], ['K'])


    def test_gen_column_decls_sql_unequal(self):
        with pytest.raises(errors.ProcessingError, match='lists must be the same length'):
            fpg.gen_column_decls_sql(['f1', 'f2', 'f3'], ['K', 'J'])


    def test_gen_column_decls_sql(self):
        sql = fpg.gen_column_decls_sql(self.cat_names, self.cat_formats)
        print(sql)
        assert sql is not None
        assert len(sql) == len(self.cat_names)
        assert sql[0] == 'ID text'
        assert sql[1] == 'RA double precision'
        assert sql[2] == 'DEC real'
        assert sql[5] == 'y integer'
        assert sql[8] == 'ccc bit'
        assert sql[9] == 'kron_flag bytea'
