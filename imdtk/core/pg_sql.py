#
# Module to interact with a PostgreSQL database.
#   Written by: Tom Hicks. 7/25/2020.
#   Last Modified: Add insert_rows_sql method. Implement fill_table* methods. Update for rename to gen_insert_row.
#
import sys

import psycopg2
from psycopg2.extras import execute_values

import imdtk.exceptions as errors
import imdtk.core.pg_gen_sql as pg_gen


def create_table (args, dbconfig, column_names, column_formats):
    """
    Create a new table using the given command line arguments,
    database parameters, and lists of column names and column formats.

    Raises ProcessingError if the column name or format vectors are not present in
    the input OR if the vectors are not the same size.
    """
    sql_list = create_table_sql(args, dbconfig, column_names, column_formats)

    db_uri = dbconfig.get('db_uri')
    conn = psycopg2.connect(db_uri)
    try:
        with conn:
            with conn.cursor() as cursor:
                for ddl in sql_list:
                    cursor.execute(ddl, [])
    finally:
        conn.close()


def create_table_str (args, dbconfig, column_names, column_formats):
    """
    Return an SQL string to create a new table using the given command line arguments,
    database parameters, and lists of column names and column formats.

    Raises ProcessingError if the column name or format vectors are not present in
    the input OR if the vectors are not the same size.
    """
    sql_list = create_table_sql(args, dbconfig, column_names, column_formats)
    return '\n'.join(sql_list)


def create_table_sql (args, dbconfig, column_names, column_formats):
    """
    Create a new table with the given table name, columns, and types as specified by
    the given catalog metadata dictionary using the given DB parameters.

    Returns a list of cleaned SQL strings to be executed to create the table
    Raises ProcessingError if the column name or format vectors are not present in
    the input OR if the vectors are not the same size.
    """
    if (column_names is not None and
        column_formats is not None and
        (len(column_names) == len(column_formats))):
        return pg_gen.gen_create_table_sql(args, dbconfig, column_names, column_formats)
    else:
        errMsg = 'Column name and format lists must be the same length.'
        raise errors.ProcessingError(errMsg)


def execute_sql (dbconfig, sql_query_string, sql_values):
    """
    Open a database connection using the given DB configuration and execute the given SQL
    format string with the given SQL values list FOR SIDE EFFECT (i.e. no values are returned).

    :param dbconfig: dictionary containing database parameters used by this method: db_uri
        Note: the given database configuration must contain a valid 'db_uri' string.
    :param sql_query_string: a valid Psycopg2 query string. This is similar to a
        standard python template string, BUT NOT THE SAME. See:
        https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
    :param sql_values: a list of values to substitute into the query string.
    """
    db_uri = dbconfig.get('db_uri')
    conn = psycopg2.connect(db_uri)
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query_string, sql_values)
    finally:
        conn.close()


def fetch_rows (dbconfig, sql_query_string, sql_values):
    """
    Open a database connection using the given DB configuration and execute the given SQL
    format string with the given SQL values, returning a list of tuples, which are the
    rows of the query result.

    :param dbconfig: dictionary containing database parameters used by this method: db_uri
        Note: the given database configuration must contain a valid 'db_uri' string.
    :param sql_query_string: a valid Psycopg2 query string. This is similar to a
        standard python template string, BUT NOT THE SAME. See:
        https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
    :param sql_value: a list of values to substitute into the query string.
    """
    db_uri = dbconfig.get('db_uri')
    conn = psycopg2.connect(db_uri)
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query_string, sql_values)
                rows = cursor.fetchall()
    finally:
        conn.close()

    return rows


def fill_table (dbconfig, data, catalog_table):
    """
    Insert the given list of data row lists into the named catalog table using
    the given DB parameters.
    """
    if (not data):                          # sanity check
        errMsg = "(fill_table): Empty data list cannot be inserted into table."
        raise errors.ProcessingError(errMsg)

    sql_fmt_str = pg_gen.gen_insert_rows(dbconfig, catalog_table)
    insert_rows_sql(dbconfig, sql_fmt_str, data)  # data already in the correct form
    return len(data)                              # assume all rows correctly inserted


def fill_table_str (dbconfig, data, catalog_table):
    """
    Return a single EXAMPLE SQL string to insert the FIRST data row ONLY into the
    named catalog table using the given DB parameters.

    Note: Because the generated SQL expects to be used by the psycopg2.extras.execute_values
          method, it cannot be correctly interpolated by the psycopg2.cursor.mogrify method
          in sql_as_string. Therefore we generate the returned SQL string manually.
    """
    sql_fmt_str = pg_gen.gen_insert_rows(dbconfig, catalog_table)
    valu = '(' + ', '.join([str(datum) for datum in data[0]]) + ')'
    return sql_fmt_str.replace('%s', valu)


def insert_hybrid_row (dbconfig, datadict, table_name):
    """
    Insert the given data dictionary into the named hybrid SQL/JSON table using the
    given DB parameters.
    """
    (sql_fmt_str, sql_values) = pg_gen.gen_hybrid_insert(dbconfig, datadict, table_name)
    execute_sql(dbconfig, sql_fmt_str, sql_values)


def insert_hybrid_row_str (dbconfig, datadict, table_name):
    """
    Return an SQL string to insert a data dictionary into the named hybrid SQL/JSON table.
    Returns None if the given data dictionary does not contain the field names required
    for the hybrid table (including the 'metadata' field).
    """
    (sql_fmt_str, sql_values) = pg_gen.gen_hybrid_insert(dbconfig, datadict, table_name)
    return sql_as_string(dbconfig, sql_fmt_str, sql_values)


def insert_row (dbconfig, datadict, table_name):
    """
    Insert the given data dictionary into the named SQL table using the given DB parameters.
    """
    (sql_fmt_str, sql_values) = pg_gen.gen_insert_row(dbconfig, datadict, table_name)
    execute_sql(dbconfig, sql_fmt_str, sql_values)


def insert_row_str (dbconfig, datadict, table_name):
    """
    Return an SQL string to insert a data dictionary into the named SQL table.
    """
    (sql_fmt_str, sql_values) = pg_gen.gen_insert_row(dbconfig, datadict, table_name)
    return sql_as_string(dbconfig, sql_fmt_str, sql_values)


def insert_rows_sql (dbconfig, sql_query_string, data_rows):
    """
    Open a database connection using the given DB configuration and execute the given
    SQL format string with the given list of rows (list of values) FOR SIDE EFFECT
    (i.e. no values are returned).

    Note: The query string MUST be compatible with the psycopg2.extras.execute_values method!

    :param dbconfig: dictionary containing database parameters used by this method: db_uri
        Note: the given database configuration must contain a valid 'db_uri' string.
    :param sql_query_string: a valid Psycopg2 query string. This is similar to a
        standard python template string, BUT NOT THE SAME. See:
        https://www.psycopg.org/docs/extras.html#psycopg2.extras.execute_values
    :param data_rows: a list of rows (list of values) to substitute into the query string.
    """
    db_uri = dbconfig.get('db_uri')
    conn = psycopg2.connect(db_uri)
    try:
        with conn:
            with conn.cursor() as cursor:
                execute_values(cursor, sql_query_string, data_rows)
    finally:
        conn.close()


def list_catalog_tables (args, dbconfig, db_schema=None):
    """
    List available image catalogs from the VOS database.

    :param args: dictionary containing context arguments used by this method: debug
    :param dbconfig: dictionary containing database parameters used by this method: db_uri
    :return a list of catalog names from the TAP schema "tables" table for the selected schema.
    """
    db_schema_name = db_schema or dbconfig.get('db_schema_name')

    catq = "SELECT table_name FROM tap_schema.tables WHERE schema_name = (%s);"

    rows = fetch_rows(dbconfig, catq, [db_schema_name])
    catalogs = [row[0] for row in rows]     # extract names from row tuples

    if (args.get('debug')):
        print("(list_catalog_tables): => '{}'".format(catalogs), file=sys.stderr)

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

    rows = fetch_rows(dbconfig, tblq, [db_schema_name])
    tables = [row[0] for row in rows]     # extract names from row tuples
    if (args.get('debug')):
        print("(pg_sql.list_table_names): => '{}'".format(tables), file=sys.stderr)

    return tables


def sql_as_string (dbconfig, sql_query_string, sql_values):
    """
    Return a query string after arguments binding. The string returned is exactly the
    one that would be sent to the database running the execute() method or similar.

    :param dbconfig: dictionary containing database parameters used by this method: db_uri
        Note: the given database configuration must contain a valid 'db_uri' string.
    :param sql_query_string: a valid Psycopg2 query string. This is similar to a
        standard python template string, BUT NOT THE SAME. See:
        https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
    :param sql_value: a list of values to substitute into the query string.
    """
    db_uri = dbconfig.get('db_uri')
    conn = psycopg2.connect(db_uri)
    try:
        with conn:
            with conn.cursor() as cursor:
                sql_byte_str = cursor.mogrify(sql_query_string, sql_values)
    finally:
        conn.close()

    return sql_byte_str.decode(encoding='utf-8')
