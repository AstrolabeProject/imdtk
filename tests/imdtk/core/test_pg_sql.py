# Tests for the PostgreSQL interface module.
#   Written by: Tom Hicks. 7/25/2020.
#   Last Modified: Update for update of PG SQL module.
#
import pytest

from config.settings import SQL_FIELDS_HYBRID
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
        "obs_collection": "JWST",
        "s_dec": 53.157662568,
        "s_ra": -27.8075199236,
        "is_public": 0,
        "metadata": {
            "file_name": "some.fits",
            "file_size": 4305,
            "timesys": "UTC",
        }
    }


    # def test_create_table_empty (self):
    #     self.args['catalog_table'] = 'test_tbl'
    #     pgsql.create_table(self.args, self.dbconfig, [], [])


    # def test_create_table (self):
    #     self.args['catalog_table'] = 'test_tbl2'
    #     ret = pgsql.create_table(self.args, self.dbconfig, self.cat_names, self.cat_formats)


    def test_create_table_str_empty (self):
        self.args['catalog_table'] = 'NEWTBL'
        tbl = pgsql.create_table_str(self.args, self.dbconfig, [], [])
        print(tbl)
        assert tbl is not None
        assert 'CREATE TABLE' in tbl
        assert 'NEWTBL' in tbl
        assert 'SET search_path TO sia' in tbl

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
        assert 'SET search_path TO sia' in tbl
        assert 'ID text' in tbl
        assert 'RA double precision' in tbl
        assert 'DEC real' in tbl
        assert 'Redshift real' in tbl
        assert 'X smallint' in tbl
        assert 'Y integer' in tbl
        assert 'A bigint' in tbl



    def test_list_table_names_schema (self):
        tbls = pgsql.list_table_names(self.args, self.dbconfig, db_schema='sia')
        print(tbls)
        assert tbls is not None
        assert len(tbls) > 0
        assert 'eazy' in tbls
        assert 'jaguar' in tbls
        assert 'jwst' in tbls
        assert 'hybrid' in tbls
        assert 'columns' not in tbls
        assert 'keys' not in tbls
        assert 'schemas' not in tbls


    def test_list_table_names (self):
        tbls = pgsql.list_table_names(self.args, self.dbconfig)
        print(tbls)
        assert tbls is not None
        assert len(tbls) > 0
        assert 'eazy' in tbls
        assert 'jaguar' in tbls
        assert 'jwst' in tbls
        assert 'hybrid' in tbls
        assert 'columns' not in tbls
        assert 'keys' not in tbls
        assert 'schemas' not in tbls


    def test_list_table_names_bad_schema (self):
        tbls = pgsql.list_table_names(self.args, self.dbconfig, db_schema='nosuch')
        print(tbls)
        assert tbls is not None
        assert len(tbls) == 0



    def test_list_catalog_tables_schema (self):
        cats = pgsql.list_catalog_tables(self.args, self.dbconfig, db_schema='sia')
        print(cats)
        assert cats is not None
        assert len(cats) > 0
        assert 'sia.eazy' in cats
        assert 'sia.jaguar' in cats
        assert 'sia.jwst' in cats
        assert 'sia.hybrid' not in cats
        assert 'sia.columns' not in cats
        assert 'sia.keys' not in cats
        assert 'sia.schemas' not in cats


    def test_list_catalog_tables (self):
        cats = pgsql.list_catalog_tables(self.args, self.dbconfig)
        print(cats)
        assert cats is not None
        assert len(cats) > 0
        assert 'sia.eazy' in cats
        assert 'sia.jaguar' in cats
        assert 'sia.jwst' in cats
        assert 'sia.hybrid' not in cats
        assert 'sia.columns' not in cats
        assert 'sia.keys' not in cats
        assert 'sia.schemas' not in cats


    def test_list_catalog_tables_bad_schema (self):
        cats = pgsql.list_catalog_tables(self.args, self.dbconfig, db_schema='nosuch')
        print(cats)
        assert cats is not None
        assert len(cats) == 0



    def test_sql_insert_str_empty (self):
        sql = pgsql.sql_insert_str(dict(), 'test_table')
        print(sql)
        assert sql is not None
        assert len(sql) > 0
        assert 'insert' in sql
        assert 'test_table' in sql
        assert 'values' in sql
        assert '();' in sql


    def test_sql_insert_str (self):
        sql = pgsql.sql_insert_str(self.datad, 'test_table')
        print(sql)
        assert sql is not None
        assert len(sql) > 175               # specific to datad table
        assert 'insert' in sql
        assert 'test_table' in sql
        assert 'values' in sql
        assert 'True' in sql
        assert 'SIMPLE' in sql
        assert 'BITPIX' in sql
        assert '-64' in sql
        assert '9791' in sql
        assert "'JWST'" in sql
        assert '53.157662568'



    def test_sql_insert_hybrid_str_empty (self):
        sql = pgsql.sql_insert_hybrid_str(dict(), 'TESTTBL')
        print(sql)
        assert sql is None


    def test_sql_insert_hybrid_str_nomd (self):
        datad_hyb_nomd = {
            "ob_collection": "JWST",
            "s_dec": 53.157662568,
            "s_ra": -27.8075199236,
            "is_public": 0
        }
        sql = pgsql.sql_insert_hybrid_str(datad_hyb_nomd, 'TESTTBL')
        print(sql)
        assert sql is None


    def test_sql_insert_hybrid_str (self):
        sql = pgsql.sql_insert_hybrid_str(self.datad_hyb, 'TESTTBL')
        print(sql)
        assert sql is not None
        print("LEN(sql)={}".format(len(sql)))
        assert len(sql) > 175               # specific to datad_hyb table
        assert 'insert' in sql
        assert 'TESTTBL' in sql
        assert 'values' in sql

        for fld in SQL_FIELDS_HYBRID:
            assert fld in sql
        assert '53.157662568' in sql
        assert '-27.8075199236' in sql

        assert 'True' not in sql
        assert 'SIMPLE' not in sql
        assert 'BITPIX' not in sql



    def test_sql4_hybrid_table_insert_empty (self):
        sql = pgsql.sql4_hybrid_table_insert(dict(), 'TESTTBL')
        print(sql)
        assert sql is None


    def test_sql4_hybrid_table_insert_nomd (self):
        datad_hyb_nomd = {
            "ob_collection": "JWST",
            "s_dec": 53.157662568,
            "s_ra": -27.8075199236,
            "is_public": 0
        }
        sql = pgsql.sql4_hybrid_table_insert(datad_hyb_nomd, 'TESTTBL')
        print(sql)
        assert sql is None


    def test_sql4_hybrid_table_insert (self):
        sql = pgsql.sql4_hybrid_table_insert(self.datad_hyb, 'TESTTBL')
        print(sql)
        assert sql is not None
        assert len(sql) == 2                # tuple of template, values

        templ = sql[0]
        assert 'insert' in templ
        assert 'TESTTBL' in templ
        assert 'values' in templ

        for fld in SQL_FIELDS_HYBRID:
            assert fld in templ

        vals = sql[1]
        assert 53.157662568 in vals
        assert -27.8075199236 in vals
        assert 'JWST' in vals

        assert 'True' not in vals
        assert 'SIMPLE' not in vals
        assert 'BITPIX' not in vals
