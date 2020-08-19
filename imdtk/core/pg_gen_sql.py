#
# Module to curate FITS data with a PostgreSQL database.
#   Written by: Tom Hicks. 7/24/2020.
#   Last Modified: Redo to clean and format fields at creation site.
#
from config.settings import DEC_ALIASES, ID_ALIASES, RA_ALIASES
import imdtk.exceptions as errors
from imdtk.core.misc_utils import missing_entries


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

# Database parameters required within this module and child modules.
REQUIRED_DB_PARAMETERS = [ 'db_schema_name', 'db_user' ]


def check_dbconfig_parameters (dbconfig, required=REQUIRED_DB_PARAMETERS):
    """
    Check the given configuration dictionary for all database parameters required by this module.

    :raises ProcessingError if a required database parameter is missing.
    """
    missing = missing_entries(dbconfig, required)
    if (missing):
        errMsg = "Missing required database parameters: {}".format(missing)
        raise errors.ProcessingError(errMsg)


def clean_id (identifier):
    """
    Clean the given SQL identifier to prevent SQL injection attacks.
    Note: that this method is specifically for simple SQL identifiers and is NOT
    a general solution which prevents SQL injection attacks.
    """
    if (identifier):
        # TODO: IMPORTANT! IMPLEMENT LATER
        return identifier
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
    check_dbconfig_parameters(dbconfig)

    # combine CLI and DB arguments for easy use with templating
    argmix = args.copy()
    argmix.update(dbconfig)

    ddl = []

    ddl.extend(gen_search_path_sql(argmix))
    ddl.extend(gen_table_sql(argmix, column_names, column_formats))
    ddl.extend(gen_table_indices_sql(argmix, column_names))

    return ddl