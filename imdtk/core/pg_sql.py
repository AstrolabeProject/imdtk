#
# Module to interact with a PostgreSQL database.
#   Written by: Tom Hicks. 7/25/2020.
#   Last Modified: Continue refactoring PostgreSQL access methods here.
#
import sys
from string import Template

import psycopg2

from config.settings import SQL_FIELDS_HYBRID
from imdtk.core.misc_utils import to_JSON


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


def make_sql_insert (datadict, table_name):
    """
    Return appropriate data structures for inserting the given data dictionary
    into a database via a database access library. Currently using Psycopg2,
    so return a tuple of an INSERT template string and a sequence of values.
    """
    keys = ', '.join(datadict.keys())
    values = list(datadict.values())
    place_holders = ', '.join(['%s' for v in values])
    template = "insert into {0} ({1}) values ({2});".format(table_name, keys, place_holders)
    return (template, values)


def make_sql_insert_hybrid (datadict, table_name):
    """
    Return appropriate data structures for inserting the given data dictionary
    into a database via a database access library. Currently using Psycopg2,
    so return a tuple of an INSERT template string and a sequence of values.
    """
    fieldnames = SQL_FIELDS_HYBRID.copy()
    fieldnames.append('metadata')       # add name of the JSON metadata field
    keys = ', '.join(fieldnames)

    values = [ datadict.get(key) for key in SQL_FIELDS_HYBRID if datadict.get(key) is not None ]
    values.append(to_JSON(datadict))    # add the JSON for the metadata field

    place_holders = ', '.join(['%s' for v in values])
    template = "insert into {0} ({1}) values ({2});".format(table_name, keys, place_holders)
    return (template, values)


def make_sql_insert_string (datadict, table_name):
    """ Return an SQL INSERT string to store the given data dictionary. """
    keys = ', '.join(datadict.keys())
    vals = datadict.values()
    values = ', '.join([ ("'{}'".format(v) if (isinstance(v, str)) else str(v)) for v in vals ])
    return "insert into {0} ({1}) values ({2});".format(table_name, keys, values)


def make_sql_insert_string_hybrid (datadict, table_name):
    """ Return an SQL INSERT string to store the given data dictionary. """
    fieldnames = SQL_FIELDS_HYBRID.copy()
    fieldnames.append('metadata')       # add name of the JSON metadata field
    keys = ', '.join(fieldnames)

    vals = [ datadict.get(key) for key in SQL_FIELDS_HYBRID if datadict.get(key) is not None ]
    vals.append(to_JSON(datadict))      # add the JSON for the metadata field
    values = ', '.join([ ("'{}'".format(v) if (isinstance(v, str)) else str(v)) for v in vals ])

    return "insert into {0} ({1}) values ({2});".format(table_name, keys, values)


def store_data (datadict, table_name, dbconfig):
    """
    Store the given data dictionary directly into the named table of the database with
    the given connection parameters.
    """
    db_uri = dbconfig.get('db_uri')         # already checked and present
    db_connection = psycopg2.connect(db_uri)
    with db_connection as conn:
        with conn.cursor() as cursor:
            (fmt_str, values) = make_sql_insert(datadict, table_name)
            cursor.execute(fmt_str, values)
    db_connection.close()


def store_data_hybrid (datadict, table_name, dbconfig):
    """
    Store the given data dictionary directly into the named table of the database with
    the given connection parameters.
    """
    db_uri = dbconfig.get('db_uri')         # already checked and present
    db_connection = psycopg2.connect(db_uri)
    with db_connection as conn:
        with conn.cursor() as cursor:
            (fmt_str, values) = make_sql_insert_hybrid(datadict, table_name)
            cursor.execute(fmt_str, values)
    db_connection.close()
