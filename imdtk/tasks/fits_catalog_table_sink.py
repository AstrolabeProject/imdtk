#
# Class to fill a DB table from the data of a FITS catalog file.
#   Written by: Tom Hicks. 8/24/2020
#   Last Modified: Better error message.
#
import sys

from config.settings import DEFAULT_DBCONFIG_FILEPATH
import imdtk.exceptions as errors
import imdtk.core.pg_sql as pg_sql
import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import STDOUT_NAME
from imdtk.tasks.i_sql_sink import ISQLSink, SQL_EXTENSION


class FitsCatalogFillTableSink (ISQLSink):
    """ Class to fill a DB table from the data of a FITS catalog file. """

    def __init__(self, args):
        """
        Constructor for class to fill a DB table from the data of a FITS catalog file.
        """
        super().__init__(args)


    #
    # Methods overriding IImdTask interface methods
    #

    def output_results (self, indata):
        """
        Store the given data into the configured database OR just output SQL
        to do so, depending on the 'sql-only' flag.
        """
        if (self._DEBUG):
            print("({}.output_results): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # load the database configuration from a given or default file path
        dbconfig_file = self.args.get('dbconfig_file') or DEFAULT_DBCONFIG_FILEPATH
        dbconfig = self.load_sql_db_config(dbconfig_file)

        # check table name to see if it is still available in the database
        catalog_table = self.args.get('catalog_table')
        if (not self.table_exists(dbconfig, catalog_table)):
            errMsg = "Catalog table to fill '{}' does not exist.".format(catalog_table)
            raise errors.ProcessingError(errMsg)

        # file information is needed by the SQL generation methods below
        file_info = md_utils.get_file_info(indata)

        # read the catalog table data from the input data structure
        data = md_utils.get_data(indata)

        # Decide whether we are creating a table in the DB or just outputting SQL statements.
        sql_only = self.args.get('sql_only')
        if (sql_only):                      # if just outputting SQL
            self.write_table(dbconfig, data, catalog_table, file_info)
        else:                               # else creating the table in the database
            self.fill_table(dbconfig, data, catalog_table)


    #
    # Non-interface and/or task-specific Methods
    #

    def table_exists (self, dbconfig, catalog_table):
        """ Return True if the named table already exists in the database, else False. """
        return catalog_table in pg_sql.list_table_names(self.args, dbconfig)


    def fill_table (self, dbconfig, data, catalog_table):
        """ Call the database-specific method to fill an existing table with the given data."""
        if (self._DEBUG):
            print("({}): Filling table: '{}'".format(self.TOOL_NAME, catalog_table), file=sys.stderr)

        # open database connection and fill the specified table
        rec_cnt = pg_sql.fill_table(dbconfig, data, catalog_table)

        if (self._VERBOSE):
            print("({}): Database table '{}' filled with {} records.".format(
                self.TOOL_NAME, catalog_table, rec_cnt), file=sys.stderr)


    def write_table (self, dbconfig, data, catalog_table, file_info):
        """ Generate and output SQL that would create a new catalog table. """
        if (self._DEBUG):
            print("({}.write_table): '{}'".format(self.TOOL_NAME, catalog_table), file=sys.stderr)

        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')
        if (genfile):                       # if generating the output filename/path
            fname = file_info.get('file_name') if file_info else "NO_FILENAME"
            outfile = self.gen_output_file_path(fname, SQL_EXTENSION, self.TOOL_NAME)
            self.write_SQL(dbconfig, data, catalog_table, file_info, outfile)
        elif (outfile is not None):         # else if using the given filepath
            self.write_SQL(dbconfig, data, catalog_table, file_info, outfile)
        else:                               # else using standard output
            self.write_SQL(dbconfig, data, catalog_table, file_info)

        if (self._VERBOSE):
            out_dest = outfile if (outfile) else STDOUT_NAME
            print("({}): SQL output to '{}'".format(self.TOOL_NAME, out_dest), file=sys.stderr)


    def write_SQL (self, dbconfig, data, catalog_table, file_info, file_path=None):
        """
        Generate and output SQL commands which would create the specified table
        in the database, using the given database configuration.
        Writes the SQL command strings to the given file path or to standard output,
        if no file path is given.
        """
        comment = self.sql_file_info_comment_str(file_info)
        fill_str = pg_sql.fill_table_str(dbconfig, data, catalog_table)
        self.output_SQL(fill_str, comment=comment, file_path=file_path)
