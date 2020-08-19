#
# Class to sink incoming image metadata to a Hybrid (SQL/JSON) PostgreSQL database.
#   Written by: Tom Hicks. 7/3/2020.
#   Last Modified: Update for changes in PG SQL module.
#
import psycopg2
import sys

from config.settings import DEFAULT_DBCONFIG_FILEPATH, DEFAULT_HYBRID_TABLE_NAME
import imdtk.exceptions as errors
import imdtk.core.pg_sql as pg_sql
import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import STDOUT_NAME
from imdtk.tasks.i_sql_sink import ISQLSink, SQL_EXTENSION


class JWST_HybridPostgreSQLSink (ISQLSink):
    """ Class to sink incoming image metadata to a Hybrid PostgreSQL database. """

    def __init__(self, args):
        """
        Constructor for class to sink incoming image metadata to a Hybrid PostgreSQL database.
        """
        super().__init__(args)


    #
    # Methods overriding IImdTask interface methods
    #

    def output_results (self, metadata):
        """
        Store the given data into the configured database OR just output SQL
        to do so, depending on the 'sql-only' flag.
        """
        if (self._DEBUG):
            print("({}.output_results): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # file information is needed by the SQL generation methods below
        file_info = md_utils.get_file_info(metadata)

        # select and/or filter the data for output
        outdata = self.select_data_for_output(metadata)

        # decide whether we are storing data in the DB or just outputting SQL statements
        sql_only = self.args.get('sql_only')
        if (sql_only):                      # if just outputting SQL
            self.write_results(outdata, file_info)
        else:                               # else storing data in a database
            self.store_results(outdata, file_info)


    #
    # Non-interface and/or task-specific Methods
    #

    def select_data_for_output (self, metadata):
        """
        Select a subset of data, from the given metadata, for output.
        Returns a single dictionary of selected data.
        """
        selected = md_utils.get_calculated(metadata).copy()
        return selected                     # return selected dataset


    def store_results (self, outdata, file_info):
        """
        Store the given data dictionary into the configured database table.
        """
        if (self._DEBUG):
            print("({}.store_results)".format(self.TOOL_NAME), file=sys.stderr)

        # load the database configuration from a given or default file path
        dbconfig_file = self.args.get('dbconfig_file') or DEFAULT_DBCONFIG_FILEPATH
        dbconfig = self.load_sql_db_config(dbconfig_file)

        # execute SQL to store the given data dictionary into the named table
        table_name = self.args.get('table_name') or DEFAULT_HYBRID_TABLE_NAME
        pg_sql.insert_hybrid_row(dbconfig, outdata, table_name)

        if (self._VERBOSE):
            print("({}): Results stored in '{}'".format(self.TOOL_NAME, table_name), file=sys.stderr)


    def write_results (self, outdata, file_info):
        """ Generate and output SQL which would save the given data dictionary. """
        if (self._DEBUG):
            print("({}.write_results)".format(self.TOOL_NAME), file=sys.stderr)

        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')
        if (genfile):                       # if generating the output filename/path
            fname = file_info.get('file_name') if file_info else "NO_FILENAME"
            outfile = self.gen_output_file_path(fname, SQL_EXTENSION, self.TOOL_NAME)
            self.write_SQL(outdata, file_info, outfile)
        elif (outfile is not None):         # else if using the given filepath
            self.write_SQL(outdata, file_info, outfile)
        else:                               # else using standard output
            self.write_SQL(outdata, file_info)

        if (self._VERBOSE):
            out_dest = outfile if (outfile) else STDOUT_NAME
            print("({}): Results output to '{}'".format(self.TOOL_NAME, out_dest), file=sys.stderr)


    def write_SQL (self, outdata, file_info, file_path=None):
        """
        Generate and output SQL commands which would insert the given data dictionary
        into the database, using the given file information dictionary.
        Writes the SQL command strings to the given file path or to standard output,
        if no file path is given.
        """
        # load the database configuration from a given or default file path
        dbconfig_file = self.args.get('dbconfig_file') or DEFAULT_DBCONFIG_FILEPATH
        dbconfig = self.load_sql_db_config(dbconfig_file)

        comment = self.sql_file_info_comment_str(file_info)
        table_name = self.args.get('table_name') or DEFAULT_HYBRID_TABLE_NAME
        insert_str = pg_sql.insert_hybrid_row_str(dbconfig, outdata, table_name)
        self.output_SQL(insert_str, comment=comment, file_path=file_path)
