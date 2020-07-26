#
# Module to interact with a PostgreSQL database.
#   Written by: Tom Hicks. 7/25/2020.
#   Last Modified: Initial creation: split out PostgreSQL access methods.
#
import sys
from string import Template

import psycopg2


def list_catalogs (args, db_schema=None):
    """
    List available image catalogs from the VOS database.

    :param args: dictionary containing database arguments used by this method:
                 verbose, DB_URI
    :return a list of catalog names from the TAP schema "tables" table for the selected schema.
    """
    db_schema_name = db_schema or args.get('db_schema_name')

    conn = psycopg2.connect(args.get('db_uri'))
    cur = conn.cursor()

    catq = "SELECT table_name FROM tap_schema.tables WHERE schema_name = (%s);"
    cur.execute(catq, [db_schema_name])
    cats = cur.fetchall()
    cur.close()
    conn.close()

    catalogs = [cat[0] for cat in cats]

    if (args.get('debug')):
        print("(list_catalogs): => '{}'".format(catalogs), file=sys.stderr)

    return catalogs


def list_table_names (args, db_schema=None):
    """
    List available tables from the VOS database.

    :param args: dictionary containing database arguments used by this method:
                 verbose, DB_URI
    :return a list of table_names for the selected schema.
    """
    db_schema_name = db_schema or args.get('db_schema_name')

    conn = psycopg2.connect(args.get('db_uri'))
    cur = conn.cursor()

    tblq = """
        SELECT c.relname as name
        FROM pg_catalog.pg_class c
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r','p','') AND n.nspname = (%s)
        ORDER by name;
    """

    cur.execute(tblq, [db_schema_name])
    tbls = cur.fetchall()
    tables = [tbl[0] for tbl in tbls]
    cur.close()
    conn.close()

    if (args.get('debug')):
        print("(pg_sql.list_table_names): => '{}'".format(tables), file=sys.stderr)

    return tables
