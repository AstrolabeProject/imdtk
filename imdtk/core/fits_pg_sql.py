#
# Module to curate FITS data with a PostgreSQL database.
#   Written by: Tom Hicks. 7/24/2020.
#   Last Modified: WIP: begin to implement table creation.
#
from string import Template


UNSUPPORTED = 'UNSUPPORTED'

# Map FITS format codes to PostgreSQL data type declarations.
#
# Format
# Code     Description                     8-bit bytes
# ------   -----------                     -----------
# L        logical (Boolean)               1
# X        bit                             *
# B        Unsigned byte                   1
# I        16-bit integer                  2
# J        32-bit integer                  4
# K        64-bit integer                  8
# A        character                       1
# E        single precision floating point 4
# D        double precision floating point 8
# C        single precision complex        8
# M        double precision complex        16
# P        array descriptor                8
# Q        array descriptor                16
#
_FITS_FORMAT_TO_SQL = {
    'A': 'text',
    'D': 'double precision',
    'E': 'real',
    'I': 'smallint',
    'J': 'integer',
    'K': 'bigint',
    'L': 'boolean',
    'X': 'bit',
    # 'B': 'Unsigned byte',
    # 'C': 'single precision complex',
    # 'M': 'double precision complex',
    # 'P': 'array descriptor',
    # 'Q': 'array descriptor',
    'B': UNSUPPORTED,
    'C': UNSUPPORTED,
    'M': UNSUPPORTED,
    'P': UNSUPPORTED,
    'Q': UNSUPPORTED
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
        pass
        # TODO: fmt_code = (parse fmt_code letter from format field)

    sql_decl = _FITS_FORMAT_TO_SQL.get(fmt_code, UNSUPPORTED)
    if (sql_decl != UNSUPPORTED):
        return sql_decl
    else:
        errMsg = "(fits_format_to_sql): FITS column format {} is not supported.".format(tform)
        raise TypeError(errMsg)


def gen_column_decls_sql (col_names, col_fmts):
    """
    Generate the SQL column declarations for a table, given lists of column names
    and FITS format specs.

    :param col_names: a list of column name strings
    :param col_fmts: a list of FITS format specifiers strings

    :return a list of SQL declaration strings for the table columns (no trailing commas!)
    :raises ValueError if the supplied argument lists are not the same size
    """
    num_names = len(col_names)
    num_fmts = len(col_fmts)
    if (num_names != num_fmts):
        errMsg = "(make_table_sql): the number of column names and column formats must be equal ({0} != {1}".format(num_names, num_fmts)
        raise ValueError(errMsg)

    col_types = [ fits_format_to_sql(fmt) for fmt in col_fmts ]
    return [ "{0} {1}".format(n, t) for n, t in zip(col_names, col_types) ]


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


def gen_search_path_sql (args):
    return [ Template('SET search_path TO ${db_schema_name}, public;').substitute(args) ]


def gen_table_indices_sql (col_names, args):
    """
    Generate and return a list of SQL statements to create indices for a table.

    :param col_names: a list of column name strings
    :param args: dictionary containing database arguments used by this method:
                 verbose, db_owner, db_schema_name, catalog_table
    """
    sql = []

    # create index on s_ra and s_dec and cluster table by that index
    if ('s_ra' in col_names and 's_dec' in col_names):
        sql.append(
            Template('CREATE INDEX ${catalog_table}_q3c_idx on ${db_schema_name}.${catalog_table} USING btree (public.q3c_ang2ipix(s_ra, s_dec));').substitute(args)
        )
        sql.append(
            Template('ALTER TABLE ${db_schema_name}.${catalog_table} CLUSTER ON ${catalog_table}_q3c_idx;').substitute(args)
        )

    # create index on the id field
    if ('id' in col_names):
        sql.append(
            Template('CREATE INDEX ${catalog_table}_id_idx on ${db_schema_name}.${catalog_table} USING btree (id);').substitute(args)
        )

    # create index on the s_dec field
    if ('s_dec' in col_names):
        sql.append(
            Template('CREATE INDEX ${catalog_table}_s_dec_idx on ${db_schema_name}.${catalog_table} USING btree (s_dec);').substitute(args)
        )

    # create index on the s_ra field
    if ('s_ra' in col_names):
        sql.append(
            Template('CREATE INDEX ${catalog_table}_s_ra_idx on ${db_schema_name}.${catalog_table} USING btree (s_ra);').substitute(args)
        )

    return sql                              # return list of SQL strings


def make_table_sql_str (args, dbconfig, col_names, col_fmts):
    """
    Generate the SQL for creating a table, given column names, FITS format specs, and
    general arguments.

    :param col_names: a list of column name strings
    :param col_fmts: a list of FITS format specifiers strings
    :param args: dictionary containing database and command line arguments

    :return a list of SQL declaration strings for the table columns (no trailing commas!)
    :raises ValueError if the supplied argument lists are not the same size
    """
    col_decls = gen_column_decls_sql(col_names, col_fmts)

    sql = []
    sql.extend(gen_search_path_sql(args))
    sql.extend(gen_create_table_sql(col_decls, args))
    sql.extend(gen_table_indices_sql(col_names, args))
    return sql
