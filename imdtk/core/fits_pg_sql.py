#
# Module to curate FITS data with a PostgreSQL database.
#   Written by: Tom Hicks. 7/24/2020.
#   Last Modified: WIP: use passed column names and formats.
#
from string import Template

import imdtk.exceptions as errors


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


def fits_format_to_sql (tform):
    """
    Map the given FITS column format field into the corresponding SQL type declaration.

    :param tform: a FITS columnn format field for translation.
    :return an SQL type declaration string, corresponding to the given FITS format code.
    :raises TypeError if tform specifies a type not supported by the database.
    """
    fmt_code = tform
    if (len(tform) > 1):
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
    :raises ValueError if the supplied argument lists are not the same size
    """
    if (len(column_names) != len(column_formats)):
        errMsg = "Column name and format lists must be the same length."
        raise errors.ProcessingError(errMsg)

    col_types = [fits_format_to_sql(fmt) for fmt in column_formats]
    return ["{0} {1}".format(n, t) for n, t in zip(column_names, col_types)]


def gen_create_table_sql (col_decls, args):
    """
    Generate and return a list of SQL statements to create a table.

    :param col_decls: a list of SQL column declaration strings
    :param args: dictionary containing database arguments used by this method:
                 db_schema_name, db_user, catalog_table
    """
    sql = []
    columns = ',\n'.join(col_decls)

    tmpl = Template('CREATE TABLE ${db_schema_name}.${catalog_table} (${columns});')
    tmpl = tmpl.safe_substitute(columns=columns)   # add columns
    sql.append(Template(tmpl).substitute(args))    # add all other variables

    sql.append(
        Template('ALTER TABLE ${db_schema_name}.${catalog_table} OWNER to ${db_user};').substitute(args)
    )

    return sql                              # return list of SQL strings


def gen_search_path_sql (dbconfig):
    """ Set the SQL search path to include the database schema from the given database parameters. """
    return [ Template('SET search_path TO ${db_schema_name}, public;').substitute(dbconfig) ]


def gen_table_indices_sql (column_names, args):
    """
    Generate and return a list of SQL statements to create indices for a table.

    :param column_names: a list of column name strings
    :param args: dictionary containing database arguments used by this method:
                 verbose, db_owner, db_schema_name, catalog_table
    """
    sql = []

    # create index on s_ra and s_dec and cluster table by that index
    if ('s_ra' in column_names and 's_dec' in column_names):
        sql.append(
            Template('CREATE INDEX ${catalog_table}_q3c_idx on ${db_schema_name}.${catalog_table} USING btree (public.q3c_ang2ipix(s_ra, s_dec));').substitute(args)
        )
        sql.append(
            Template('ALTER TABLE ${db_schema_name}.${catalog_table} CLUSTER ON ${catalog_table}_q3c_idx;').substitute(args)
        )

    # create index on the id field
    if ('id' in column_names):
        sql.append(
            Template('CREATE INDEX ${catalog_table}_id_idx on ${db_schema_name}.${catalog_table} USING btree (id);').substitute(args)
        )

    # create index on the s_dec field
    if ('s_dec' in column_names):
        sql.append(
            Template('CREATE INDEX ${catalog_table}_s_dec_idx on ${db_schema_name}.${catalog_table} USING btree (s_dec);').substitute(args)
        )

    # create index on the s_ra field
    if ('s_ra' in column_names):
        sql.append(
            Template('CREATE INDEX ${catalog_table}_s_ra_idx on ${db_schema_name}.${catalog_table} USING btree (s_ra);').substitute(args)
        )

    return sql                              # return list of SQL strings


def make_table_sql_str (args, dbconfig, column_names, column_formats):
    """
    Generate the SQL for creating a table, given column names, FITS format specs, and
    general arguments.

    :param column_names: a list of column name strings
    :param column_formats: a list of FITS format specifiers strings
    :param args: dictionary containing command line arguments
    :param dbconfig: dictionary containing database parameters

    :return a list of SQL declaration strings for the table columns (no trailing commas!)
    :raises ValueError if the supplied argument lists are not the same size
    """
    col_decls = gen_column_decls_sql(column_names, column_formats)

    sql = []
    sql.extend(gen_search_path_sql(dbconfig))
    sql.extend(gen_create_table_sql(col_decls, args))
    sql.extend(gen_table_indices_sql(column_names, args))
    return sql
