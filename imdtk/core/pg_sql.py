#
# Module to interact with a PostgreSQL database.
#   Written by: Tom Hicks. 7/25/2020.
#   Last Modified: Refactor: consolidate and rename SQL generation and output methods.
#
import sys
from string import Template

import psycopg2

from config.settings import SQL_FIELDS_HYBRID
from imdtk.core.misc_utils import to_JSON


def execute_sql (dbconfig, sql_format_string, sql_values):
    """
    Open a database connection using the given DB configuration and execute the given SQL
    format string with the given SQL values FOR SIDE EFFECT (i.e. no values are returned).

    :param dbconfig: dictionary containing database parameters used by this method: db_uri
        Note: the given database configuration must contain a valid 'db_uri' string.
    """
    db_uri = dbconfig.get('db_uri')
    db_connection = psycopg2.connect(db_uri)
    try:
        with db_connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_format_string, sql_values)
    finally:
        db_connection.close()


def list_catalogs (args, dbconfig, db_schema=None):
    """
    List available image catalogs from the VOS database.

    :param args: dictionary containing context arguments used by this method: debug
    :param dbconfig: dictionary containing database parameters used by this method: db_uri
    :return a list of catalog names from the TAP schema "tables" table for the selected schema.
    """
    db_schema_name = db_schema or dbconfig.get('db_schema_name')

    catq = "SELECT table_name FROM tap_schema.tables WHERE schema_name = (%s);"

    db_uri = dbconfig.get('db_uri')         # already checked and present
    db_connection = psycopg2.connect(db_uri)
    try:
        with db_connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(catq, [db_schema_name])
                cats = cursor.fetchall()
    finally:
        db_connection.close()

    catalogs = [cat[0] for cat in cats]     # extract names from wrappers

    if (args.get('debug')):
        print("(list_catalogs): => '{}'".format(catalogs), file=sys.stderr)

    return catalogs


def list_table_names (args, dbconfig, db_schema=None):
    """
    List available tables from the VOS database.

    :param args: dictionary containing context arguments used by this method: debug
    :param dbconfig: dictionary containing database parameters used by this method: db_uri
    :return a list of table_names for the selected schema.
    """
    db_schema_name = db_schema or dbconfig.get('db_schema_name')

    tblq = """
        SELECT c.relname as name
        FROM pg_catalog.pg_class c
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r','p','') AND n.nspname = (%s)
        ORDER by name;
    """

    db_uri = dbconfig.get('db_uri')         # already checked and present
    db_connection = psycopg2.connect(db_uri)
    try:
        with db_connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(tblq, [db_schema_name])
                tbls = cursor.fetchall()
    finally:
        db_connection.close()

    tables = [tbl[0] for tbl in tbls]       # extract names from wrappers

    if (args.get('debug')):
        print("(pg_sql.list_table_names): => '{}'".format(tables), file=sys.stderr)

    return tables


def sql_insert_str (datadict, table_name):
    """
    Return an SQL string to insert a data dictionary into the named SQL table.

    Note: the returned string is for debugging only and IS NOT SQL-INJECTION safe.
    """
    keys = ', '.join(datadict.keys())
    vals = datadict.values()
    values = ', '.join([ ("'{}'".format(v) if (isinstance(v, str)) else str(v)) for v in vals ])
    return "insert into {0} ({1}) values ({2});".format(table_name, keys, values)


def sql_insert_hybrid_str (datadict, table_name):
    """
    Return an SQL string to insert a data dictionary into the named hybrid SQL/JSON table.

    Note: the returned string is for debugging only and IS NOT SQL-INJECTION safe.
    """
    fieldnames = SQL_FIELDS_HYBRID.copy()
    fieldnames.append('metadata')       # add name of the JSON metadata field
    keys = ', '.join(fieldnames)

    vals = [ datadict.get(key) for key in SQL_FIELDS_HYBRID if datadict.get(key) is not None ]
    vals.append(to_JSON(datadict, sort_keys=True))  # add the JSON for the metadata field
    values = ', '.join([ ("'{}'".format(v) if (isinstance(v, str)) else str(v)) for v in vals ])

    return "insert into {0} ({1}) values ({2});".format(table_name, keys, values)


def sql4_table_insert (datadict, table_name):
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


def sql4_hybrid_table_insert (datadict, table_name):
    """
    Return appropriate data structures for inserting the given data dictionary
    into a database via a database access library. Currently using Psycopg2,
    so return a tuple of an INSERT template string and a sequence of values.
    """
    fieldnames = SQL_FIELDS_HYBRID.copy()
    fieldnames.append('metadata')       # add name of the JSON metadata field
    keys = ', '.join(fieldnames)

    values = [ datadict.get(key) for key in SQL_FIELDS_HYBRID if datadict.get(key) is not None ]
    values.append(to_JSON(datadict, sort_keys=True))  # add the JSON for the metadata field

    place_holders = ', '.join(['%s' for v in values])
    template = "insert into {0} ({1}) values ({2});".format(table_name, keys, place_holders)
    return (template, values)


def store_to_table (dbconfig, datadict, table_name):
    """
    Insert the given data dictionary into the named SQL table using the given DB parameters.
    """
    (sql_fmt_str, sql_values) = sql4_table_insert(datadict, table_name)
    execute_sql(dbconfig, sql_fmt_str, sql_values)


def store_to_hybrid_table (dbconfig, datadict, table_name):
    """
    Insert the given data dictionary into the named hybrid SQL/JSON table using the
    given DB parameters.
    """
    (sql_fmt_str, sql_values) = sql4_hybrid_table_insert(datadict, table_name)
    execute_sql(dbconfig, sql_fmt_str, sql_values)
