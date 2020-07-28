# Tests for the PostgreSQL interface module.
#   Written by: Tom Hicks. 7/25/2020.
#   Last Modified: Update tests for list_catalog_tables rename.
#
import pytest

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
