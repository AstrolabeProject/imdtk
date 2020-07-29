# Tests for the PostgreSQL interface module.
#   Written by: Tom Hicks. 7/25/2020.
#   Last Modified: Add tests for sql_insert_str, sql_insert_hybrid_str, sql4_hybrid_table_insert
#                  and stubs for sql_create_table and sql_create_table_str.
#
import pytest

from config.settings import SQL_FIELDS_HYBRID
import imdtk.core.pg_sql as pgsql


class TestPgSql(object):

    args = { 'debug': True, 'verbose': True }
    dbargs = {
        # 'db_host': 'pgdb',
        # 'db_name': 'vos',
        # 'db_port': '5432',
        # 'db_pwd': 'changeMe',
        # 'db_user': 'astrolabe',
        'db_schema_name': 'sia',
        'db_uri': 'postgresql://astrolabe:changeMe@pgdb:5432/vos'
    }

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


    def test_list_table_names_schema (self):
        tbls = pgsql.list_table_names(self.args, self.dbargs, db_schema='sia')
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
        tbls = pgsql.list_table_names(self.args, self.dbargs)
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
        tbls = pgsql.list_table_names(self.args, self.dbargs, db_schema='nosuch')
        print(tbls)
        assert tbls is not None
        assert len(tbls) == 0



    def test_list_catalog_tables_schema (self):
        cats = pgsql.list_catalog_tables(self.args, self.dbargs, db_schema='sia')
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
        cats = pgsql.list_catalog_tables(self.args, self.dbargs)
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
        cats = pgsql.list_catalog_tables(self.args, self.dbargs, db_schema='nosuch')
        print(cats)
        assert cats is not None
        assert len(cats) == 0



    def test_sql_create_table_empty (self):
        tbl = pgsql.sql_create_table(self.dbargs, dict(), 'new_tbl')
        assert tbl is not None
        assert tbl == "-- Creating table 'new_tbl'"


    def test_sql_create_table (self):
        tbl = pgsql.sql_create_table(self.dbargs, dict(), 'new_tbl')
        assert tbl is not None
        assert tbl == "-- Creating table 'new_tbl'"



    def test_sql_create_table_str_empty (self):
        tbl = pgsql.sql_create_table_str(dict(), 'NEWTBL')
        assert tbl is not None
        assert tbl == "-- SQL string for creating table 'NEWTBL'"


    def test_sql_create_table_str (self):
        tbl = pgsql.sql_create_table_str(self.dbargs, 'NEWTBL')
        assert tbl is not None
        assert tbl == "-- SQL string for creating table 'NEWTBL'"



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
