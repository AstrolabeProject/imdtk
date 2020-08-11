#
# Module to curate FITS data with a PostgreSQL database.
#   Written by: Tom Hicks. 7/24/2020.
#   Last Modified: Rename some generation methods, for consistency.
#
from string import Template

from config.settings import DEC_ALIASES, ID_ALIASES, RA_ALIASES
import imdtk.exceptions as errors
from imdtk.core.misc_utils import missing_entries


UNSUPPORTED = 'UNSUPPORTED'

# Map FITS format codes to PostgreSQL data type declarations.
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
    return ["{0} {1}".format(n, t) for n, t in zip(column_names, col_types)]


def gen_table_sql (argmix, dbconfig, col_decls):
    """
    Generate and return a list of SQL statements to create a table.

    :param col_decls: a list of SQL column declaration strings
    :param argmix: dictionary containing both CLI and database arguments used by this method:
                   db_schema_name, db_user, catalog_table
    """
    sql = []
    columns = ',\n'.join(col_decls)

    tmpl = Template('CREATE TABLE ${db_schema_name}.${catalog_table} (${columns});')
    tmpl = tmpl.safe_substitute(columns=columns)   # add columns: return incomplete template
    sql.append(Template(tmpl).substitute(argmix))  # add all other variables

    sql.append(
        Template('ALTER TABLE ${db_schema_name}.${catalog_table} OWNER to ${db_user};').substitute(argmix)
    )

    return sql                              # return list of SQL strings


def gen_search_path_sql (dbconfig):
    """
    Set the SQL search path to include the database schema from the given database parameters.

    :param dbconfig: dictionary containing database arguments used by this method:
                   db_schema_name
    """
    return [ Template('SET search_path TO ${db_schema_name}, public;').substitute(dbconfig) ]


def gen_table_indices_sql (argmix, dbconfig, column_names):
    """
    Generate and return a list of SQL statements to create indices for a table.

    :param column_names: a list of column name strings
    :param argmix: dictionary containing both CLI and database arguments used by this method:
                   verbose, db_schema_name, catalog_table
    """
    sql = []

    # find DEC, RA, and ID aliases while maintaining column name order:
    dec_names = []
    id_names = []
    ra_names = []

    for col_name in column_names:
        if (col_name in DEC_ALIASES):
            dec_names.append(col_name)

        if (col_name in RA_ALIASES):
            ra_names.append(col_name)

        if (col_name in ID_ALIASES):
            id_names.append(col_name)

    first_dec = dec_names[0] if (len(dec_names) > 0) else None
    first_ra = ra_names[0] if (len(ra_names) > 0) else None

    # create index on first RA and first DEC and cluster the table by that index
    if (first_dec and first_ra):
        sql.append(
            Template('CREATE INDEX ${catalog_table}_q3c_idx on ${db_schema_name}.${catalog_table} USING btree (public.q3c_ang2ipix(${fr}, ${fd}));').substitute(argmix, fr=first_ra, fd=first_dec)
        )
        sql.append(
            Template('ALTER TABLE ${db_schema_name}.${catalog_table} CLUSTER ON ${catalog_table}_q3c_idx;').substitute(argmix)
        )

    # create indices on any ID field
    for fld in id_names:
        sql.append(
            Template('CREATE INDEX ${catalog_table}_${id}_idx on ${db_schema_name}.${catalog_table} USING btree (${id});').substitute(argmix, id=fld)
        )

    # create indices on any DEC field
    for fld in dec_names:
        sql.append(
            Template('CREATE INDEX ${catalog_table}_${dec}_idx on ${db_schema_name}.${catalog_table} USING btree (${dec});').substitute(argmix, dec=fld)
        )

    # create indices on any RA field
    for fld in ra_names:
        sql.append(
            Template('CREATE INDEX ${catalog_table}_${ra}_idx on ${db_schema_name}.${catalog_table} USING btree (${ra});').substitute(argmix, ra=fld)
        )

    return sql                              # return list of SQL strings


def gen_create_table_sql_str (args, dbconfig, column_names, column_formats):
    """
    Generate the SQL for creating a table, given column names, FITS format specs, and
    general arguments.

    :param column_names: a list of column name strings
    :param column_formats: a list of FITS format specifiers strings
    :param args: dictionary containing command line arguments
    :param dbconfig: dictionary containing database parameters

    :return a list of SQL declaration strings for the table columns (no trailing commas!)
    :raises ProcessingError if any database parameters required by this module are missing.
    """
    # raise error is any required database parameters are missing
    check_dbconfig_parameters(dbconfig)

    # combine CLI and DB arguments for easy use with templates
    argmix = args.copy()
    argmix.update(dbconfig)

    sql = []

    col_decls = gen_column_decls_sql(column_names, column_formats)
    sql.extend(gen_search_path_sql(dbconfig))
    sql.extend(gen_table_sql(argmix, dbconfig, col_decls))
    sql.extend(gen_table_indices_sql(argmix, dbconfig, column_names))

    return sql
