#
# Module to curate FITS data with a PostgreSQL database.
#   Written by: Tom Hicks. 7/24/2020.
#   Last Modified: Rename method to gen_insert_row. Add gen_insert_rows method.
#
from config.settings import DEC_ALIASES, ID_ALIASES, RA_ALIASES, SQL_FIELDS_HYBRID
import imdtk.exceptions as errors
from imdtk.core.misc_utils import keep_characters, missing_entries, to_JSON
from string import ascii_letters, digits


UNSUPPORTED = 'UNSUPPORTED'

# Map FITS format codes (TDISPn keywords) to PostgreSQL data type declarations.
#
# Format
# Code     Description                     8-bit bytes
# ------   -----------                     -----------
# A        character                       1
# B        Unsigned byte                   1
# C        single precision complex        8
# D        double precision floating point 8
# E        single precision floating point 4
# F        single precision floating point 4
# I        16-bit integer                  2
# J        32-bit integer                  4
# K        64-bit integer                  8
# L        logical (Boolean)               1
# M        double precision complex        16
# O        octal integer                   1
# P        array descriptor                8
# Q        array descriptor                16
# X        bit                             *
# Z        hexadecimal integer             1
#
_FITS_FORMAT_TO_SQL = {
    'A': 'text',
    'D': 'double precision',
    'E': 'real',
    'F': 'real',
    'I': 'smallint',
    'J': 'integer',
    'K': 'bigint',
    'L': 'boolean',
    'O': 'bytea',
    'X': 'bit',
    'Z': 'bytea',
    'B': UNSUPPORTED,  # 'Unsigned byte',
    'C': UNSUPPORTED,  # 'single precision complex',
    'M': UNSUPPORTED,  # 'double precision complex',
    'P': UNSUPPORTED,  # 'array descriptor',
    'Q': UNSUPPORTED,  # 'array descriptor'
}

# Restricted set of characters allowed for database identifiers by cleaning function
DB_ID_CHARS = set(ascii_letters + digits + '_')

# Database parameters required within this module and child modules.
REQUIRED_DB_PARAMETERS = [ 'db_schema_name', 'db_user' ]


def check_missing_parameters (config, required=REQUIRED_DB_PARAMETERS):
    """
    Check the given configuration dictionary for all database parameters required by this module.

    :raises ProcessingError if a required database parameter is missing.
    """
    missing = missing_entries(config, required)
    if (missing):
        errMsg = "Missing required parameters: {}".format(missing)
        raise errors.ProcessingError(errMsg)


def clean_id (identifier, allowed=DB_ID_CHARS):
    """
    Clean the given SQL identifier to prevent SQL injection attacks.
    Note: that this method is specifically for simple SQL identifiers and is NOT
    a general solution which prevents SQL injection attacks.
    """
    if (identifier):
        return keep_characters(identifier, allowed)
    else:
        errMsg = "Identifier to be cleaned cannot be empty or None."
        raise errors.ProcessingError(errMsg)


def fits_format_to_sql (tform):
    """
    Map the given FITS column format field into the corresponding SQL type declaration.

    :param tform: a FITS columnn format field for translation.
    :return an SQL type declaration string, corresponding to the given FITS format code.
    :raises ProcessingError if tform specifies a type not supported by the database.
    """
    fmt_code = tform
    if (tform and len(tform) > 1):
        fmt_code = tform[0:1]

    sql_decl = _FITS_FORMAT_TO_SQL.get(fmt_code, UNSUPPORTED)
    if (sql_decl != UNSUPPORTED):
        return sql_decl
    else:
        errMsg = "FITS data column format '{}' is not supported.".format(tform)
        raise errors.ProcessingError(errMsg)


def gen_column_decls_sql (column_names, column_formats):
    """
    Generate the SQL column declarations for a table, given lists of column names
    and FITS format specs.

    :param column_names: a list of column name strings
    :param column_formats: a list of FITS format specifiers strings

    :return a list of SQL declaration strings for the table columns (no trailing commas!)
    :raises ProcessingError if the given column name and format lists are not the same size.
    """
    if (len(column_names) != len(column_formats)):
        errMsg = "Column name and format lists must be the same length."
        raise errors.ProcessingError(errMsg)

    col_types = [fits_format_to_sql(fmt) for fmt in column_formats]
    col_names_clean = [clean_id(name) for name in column_names]  # clean the column names
    return ["{0} {1}".format(n, t) for n, t in zip(col_names_clean, col_types)]


def gen_create_table_sql (args, dbconfig, column_names, column_formats):
    """
    Generate the SQL for creating a table, given column names, FITS format specs, and
    general arguments.

    :param args: dictionary containing command line arguments.
    :param dbconfig: dictionary containing database parameters.
    :param column_names: a list of column name strings.
    :param column_formats: a list of FITS format specifiers strings.

    :return a list of SQL declaration strings for the table columns (no trailing commas!)
    :raises ProcessingError if any database parameters required by this module are missing.
    """
    # raise error is any required database parameters are missing
    check_missing_parameters(dbconfig)

    # combine CLI and DB arguments for easy use with templating
    argmix = args.copy()
    argmix.update(dbconfig)

    ddl = []

    ddl.extend(gen_search_path_sql(argmix))
    ddl.extend(gen_table_sql(argmix, column_names, column_formats))
    ddl.extend(gen_table_indices_sql(argmix, column_names))

    return ddl


def gen_hybrid_insert (dbconfig, datadict, table_name):
    """
    Return appropriate data structures for inserting the given data dictionary
    into a database via a database access library. Currently using Psycopg2,
    so return a tuple of an INSERT template string and a sequence of values.

    Returns (None, None) if the given data dictionary does not contain the field
    names required for the hybrid table (including the 'metadata' field).
    """
    if (not datadict):                      # sanity check
        errMsg = "(gen_hybrid_insert): Empty data dictionary cannot be inserted into table."
        raise errors.ProcessingError(errMsg)

    schema_clean = clean_id(dbconfig.get('db_schema_name'))
    table_clean = clean_id(table_name)

    required = SQL_FIELDS_HYBRID.copy()
    fieldnames = [clean_id(field) for field in required]
    num_keys = len(fieldnames)              # number of keys minus 1 (w/o metadata)
    fieldnames.append('metadata')           # add name of the JSON metadata field
    keys = ', '.join(fieldnames)            # made from cleaned fieldnames

    values = [ datadict.get(key) for key in required if datadict.get(key) is not None ]
    num_vals = len(values)                  # number of values minus 1 (no metadata yet)
    if (num_keys == num_vals):              # must have a value for each key
        values.append(to_JSON(datadict, sort_keys=True))  # add the JSON for the metadata field
        place_holders = ', '.join(['%s' for v in values])
        sql_fmt_str = "insert into {0}.{1} ({2}) values ({3});".format(schema_clean, table_clean, keys, place_holders)
        return (sql_fmt_str, values)
    else:                                   # there was a mismatch of keys and values
        errMsg = "Unable to find values for all {} required fields: {}".format(num_keys, required)
        raise errors.ProcessingError(errMsg)


def gen_insert_row (dbconfig, datadict, table_name):
    """
    Return appropriate data structures for inserting the given data dictionary
    into a database via a database access library. Currently using Psycopg2,
    so return a tuple of an INSERT template string and a sequence of values.
    """
    if (not datadict):                      # sanity check
        errMsg = "(gen_insert_row): Empty data dictionary cannot be inserted into table."
        raise errors.ProcessingError(errMsg)

    schema_clean = clean_id(dbconfig.get('db_schema_name'))
    table_clean = clean_id(table_name)

    keys_clean = [clean_id(key) for key in datadict.keys()]
    keys = ', '.join(keys_clean)

    values = list(datadict.values())
    place_holders = ', '.join(['%s' for v in values])
    sql_fmt_str = "insert into {0}.{1} ({2}) values ({3});".format(schema_clean, table_clean, keys, place_holders)
    return (sql_fmt_str, values)


def gen_insert_rows (dbconfig, table_name):
    """
    Return appropriate data structures for later inserting a list of rows
    into a database via a database access library. Currently using Psycopg2, so return
    an INSERT template string which can later be used to insert a sequence of values.

    Note: The generated SQL expects to be used by the psycopg2.extras.execute_values() method!
          This makes it incompatible with the rest of the psycopg2 "execute" methods.
    """
    schema_clean = clean_id(dbconfig.get('db_schema_name'))
    table_clean = clean_id(table_name)
    return "insert into {0}.{1} values %s;".format(schema_clean, table_clean)


def gen_search_path_sql (argmix):
    """
    Set the SQL search path to include the database schema from the given database parameters.

    :param argmix: dictionary containing database arguments used by this method:
                   db_schema_name
    :return: a list of SQL statements to execute to add the configured schema to the search path.
    """
    schema_clean = clean_id(argmix.get('db_schema_name'))
    return [ "SET search_path TO {}, public;".format(schema_clean) ]


def gen_table_sql (argmix, column_names, column_formats):
    """
    Generate and return a list of SQL statements to create a table.

    :param argmix: dictionary containing both CLI and database arguments used by this method:
                   catalog_table, db_schema_name, db_user
    :param column_names: a list of column name strings.
    :param column_formats: a list of FITS format specifiers strings.
    :return: a list of SQL statements to execute to create the table.
    """
    ddl = []                                # hold list of SQL statements to execute

    col_decls = gen_column_decls_sql(column_names, column_formats)  # already cleaned
    columns = ',\n'.join(col_decls)

    cattbl_clean = clean_id(argmix.get('catalog_table'))
    dbuser_clean  = clean_id(argmix.get('db_user'))
    schema_clean = clean_id(argmix.get('db_schema_name'))

    ctable = "CREATE TABLE {0}.{1} ({2});".format(schema_clean, cattbl_clean, columns)
    ddl.append(ctable)

    altable = "ALTER TABLE {0}.{1} OWNER to {2};".format(schema_clean, cattbl_clean, dbuser_clean)
    ddl.append(altable)

    return ddl                              # return list of SQL statements to execute


def gen_table_indices_sql (argmix, column_names):
    """
    Generate and return a list of SQL statements to create indices for a table.

    :param argmix: dictionary containing both CLI and database arguments used by this method:
                   catalog_table, db_schema_name, verbose
    :param column_names: a list of column name strings.
    :return: a list of SQL statements to execute to create indices for the table.
    """
    ddl = []

    # find DEC, RA, and ID aliases while maintaining column name order:
    dec_names = []
    id_names = []
    ra_names = []

    # clean the column names
    col_names_clean = [clean_id(name) for name in column_names]

    for col_name in col_names_clean:
        if (col_name in DEC_ALIASES):
            dec_names.append(col_name)

        if (col_name in RA_ALIASES):
            ra_names.append(col_name)

        if (col_name in ID_ALIASES):
            id_names.append(col_name)

    first_dec = dec_names[0] if (len(dec_names) > 0) else None
    first_ra = ra_names[0] if (len(ra_names) > 0) else None

    cattbl_clean = clean_id(argmix.get('catalog_table'))
    dbuser_clean  = clean_id(argmix.get('db_user'))
    schema_clean = clean_id(argmix.get('db_schema_name'))

    # create index on first RA and first DEC and cluster the table by that index
    if (first_dec and first_ra):
        ddl.append(
            "CREATE INDEX {0}_q3c_idx on {1}.{2} USING btree (public.q3c_ang2ipix({3}, {4}));".format(cattbl_clean, schema_clean, cattbl_clean, first_ra, first_dec) )

        ddl.append(
            "ALTER TABLE {0}.{1} CLUSTER ON {2}_q3c_idx;".format(schema_clean, cattbl_clean, cattbl_clean) )

    # create indices on any ID field
    for idn in id_names:
        ddl.append(
            "CREATE INDEX {0}_{1}_idx on {2}.{3} USING btree ({4});".format(cattbl_clean, idn, schema_clean, cattbl_clean, idn) )

    # create indices on any DEC field
    for dec in dec_names:
        ddl.append(
            "CREATE INDEX {0}_{1}_idx on {2}.{3} USING btree ({4});".format(cattbl_clean, dec, schema_clean, cattbl_clean, dec) )

    # create indices on any RA field
    for ra in ra_names:
        ddl.append(
            "CREATE INDEX {0}_{1}_idx on {2}.{3} USING btree ({4});".format(cattbl_clean, ra, schema_clean, cattbl_clean, ra) )

    return ddl                              # return list of SQL strings
