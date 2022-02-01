# Tests for the PostgreSQL interface module.
#   Written by: Tom Hicks. 7/25/2020.
#   Last Modified: Update for "core" and "other" SQL fields.
#
import pytest

from config.settings import CORE_SQL_FIELDS, OTHER_SQL_FIELDS
import imdtk.exceptions as errors
import imdtk.core.pg_sql as pgsql
import imdtk.tasks.i_sql_sink as isql
from tests import TEST_DBCONFIG_FILEPATH


class TestPgSql(object):

    args = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestPgSql', 'catalog_table': 'myCatalog' }

    # load DB test configuration parameters
    task = isql.ISQLSink(args)
    dbconfig = task.load_sql_db_config(TEST_DBCONFIG_FILEPATH)
    print("TestPgSql:dbconfig={}".format(dbconfig))

    cat_names = [
        "ID",
        "RA",
        "DEC",
        "Redshift",
        "X",
        "Y",
        "A",
        "BB",
        "CCC",
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

    datad = {
        "SIMPLE": True,
        "BITPIX": -64,
        "NAXIS": 2,
        "NAXIS1": 9791,
        "NAXIS2": 4305,
        "INSTRUME": "JWST",
        "TIMESYS": "UTC",
        "WCSAXES": 2,
        "CRVAL1": 53.157662568,
        "CRVAL2": -27.8075199236
    }

    datad_hyb = {
        "md5sum" : 'fe57e89d674e1e52071f674c60974968',  # m13.fits
        "s_dec": 53.157662568,
        "s_ra": -27.8075199236,
        "is_public": False,
        "obs_collection": "TEST2",
        "file_name": "some.fits",
        "file_size": 4305,
        "md": {
            "file_name": "some.fits",
            "file_size": 4305,
            "filter": "F444W",
            "timesys": "UTC",
        }
    }


    def test_create_table_str_empty (self):
        self.args['catalog_table'] = 'NEWTBL'
        tbl = pgsql.create_table_str(self.args, self.dbconfig, [], [])
        print(tbl)
        assert tbl is not None
        assert 'CREATE TABLE' in tbl
        assert 'NEWTBL' in tbl
        assert 'SET search_path TO public' in tbl

        assert 'ID text' not in tbl
        assert 'RA double precision' not in tbl
        assert 'DEC real' not in tbl


    def test_create_table_str (self):
        self.args['catalog_table'] = 'NEWTBL'
        tbl = pgsql.create_table_str(self.args, self.dbconfig, self.cat_names, self.cat_formats)
        print(tbl)
        assert tbl is not None
        assert 'CREATE TABLE' in tbl
        assert 'NEWTBL' in tbl
        assert 'SET search_path TO public' in tbl
        assert 'ID text' in tbl
        assert 'RA double precision' in tbl
        assert 'DEC real' in tbl
        assert 'Redshift real' in tbl
        assert 'X smallint' in tbl
        assert 'Y integer' in tbl
        assert 'A bigint' in tbl



    def test_list_table_names_schema (self):
        tbls = pgsql.list_table_names(self.args, self.dbconfig, db_schema='public')
        print(tbls)
        assert tbls is not None
        assert len(tbls) > 0
        assert 'imgmd' in tbls
        assert 'collections' not in tbls
        assert 'jwst' not in tbls
        assert 'hybrid' not in tbls
        assert 'columns' not in tbls
        assert 'keys' not in tbls
        assert 'schemas' not in tbls


    def test_list_table_names (self):
        tbls = pgsql.list_table_names(self.args, self.dbconfig)
        print(tbls)
        assert tbls is not None
        assert len(tbls) > 0
        assert 'imgmd' in tbls
        assert 'collections' not in tbls
        assert 'jwst' not in tbls
        assert 'hybrid' not in tbls
        assert 'columns' not in tbls
        assert 'keys' not in tbls
        assert 'schemas' not in tbls


    def test_list_table_names_bad_schema (self):
        tbls = pgsql.list_table_names(self.args, self.dbconfig, db_schema='nosuch')
        print(tbls)
        assert tbls is not None
        assert len(tbls) == 0


    def test_insert_row_str_empty (self):
        with pytest.raises(errors.ProcessingError, match='cannot be inserted'):
            pgsql.insert_row_str(self.dbconfig, dict(), 'test_table')
        # print(sql)
        # assert sql is not None
        # assert len(sql) > 0
        # assert 'insert' in sql
        # assert 'test_table' in sql
        # assert 'values' in sql
        # assert '();' in sql


    def test_insert_row_str (self):
        sql = pgsql.insert_row_str(self.dbconfig, self.datad, 'test_table')
        print(sql)
        assert sql is not None
        assert len(sql) > 175               # specific to datad table
        assert 'insert' in sql
        assert 'test_table' in sql
        assert 'values' in sql
        assert 'true' in sql
        assert 'SIMPLE' in sql
        assert 'BITPIX' in sql
        assert '-64' in sql
        assert '9791' in sql
        assert "'JWST'" in sql
        assert '53.157662568'



    def test_insert_hybrid_row_str_empty (self):
        with pytest.raises(errors.ProcessingError, match='cannot be inserted'):
            pgsql.insert_hybrid_row_str(self.dbconfig, dict(), 'TESTTBL')


    def test_insert_hybrid_row_str_min (self):
        datad_hyb_min = {
            "md5sum": "2c9202ae878ecfcb60878ceb63837f5f",  # HorseHead.fits
            "s_dec": 53.157662568,
            "s_ra": -27.8075199236,
            "is_public": False,
            "obs_collection": "TEST",
            "file_name": "HorseHead.fits",
            "file_size": 1650240,
        }
        sql = pgsql.insert_hybrid_row_str(self.dbconfig, datad_hyb_min, 'test_tbl')
        print(sql)
        assert 'insert' in sql
        assert 'test_tbl' in sql
        assert 's_dec' in sql
        assert 'is_public' in sql
        assert 'values' in sql
        assert '53.157662568' in sql
        assert '-27.8075199236' in sql

        assert 'true' not in sql
        assert 'SIMPLE' not in sql
        assert 'BITPIX' not in sql


    def test_insert_hybrid_row_str (self):
        sql = pgsql.insert_hybrid_row_str(self.dbconfig, self.datad_hyb, 'TESTTBL')
        print(sql)
        assert sql is not None
        print("LEN(sql)={}".format(len(sql)))
        assert len(sql) > 175               # specific to datad_hyb table
        assert 'insert' in sql
        assert 'TESTTBL' in sql
        assert 'values' in sql

        for fld in CORE_SQL_FIELDS:
            assert fld in sql
        for fld in OTHER_SQL_FIELDS:
            assert fld in sql
        assert '53.157662568' in sql
        assert '-27.8075199236' in sql

        assert 'true' not in sql
        assert 'SIMPLE' not in sql
        assert 'BITPIX' not in sql


    def test_insert_hybrid_row_str_noval (self):
        datad_hyb_min = {
            "md5sum": "fe57e89d674e1e52071f674c60974968",  # m13.fits
            "s_dec": 53.157662568,
            "s_ra": -27.8075199236,
            "is_public": None,
        }
        with pytest.raises(errors.ProcessingError, match='Unable to find .* required fields'):
            pgsql.insert_hybrid_row_str(self.dbconfig, datad_hyb_min, 'test_tbl')
