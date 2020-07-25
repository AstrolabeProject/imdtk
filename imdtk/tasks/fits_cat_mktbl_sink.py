#
# Class to create a new database table from the metadata of a FITS catalog file.
#   Written by: Tom Hicks. 7/22/2020.
#   Last Modified: WIP: refactor some non-DB specific SQL methods to parent SQL class.
#
import configparser
import psycopg2
import sys

from config.settings import DEFAULT_DBCONFIG_FILEPATH
import imdtk.exceptions as errors
import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import STDOUT_NAME
from imdtk.tasks.i_sql_sink import ISQLSink, SQL_EXTENSION


class FitsCatalogTableSink (ISQLSink):
    """ Class to create a new DB table from metadata of a FITS catalog file. """

    def __init__(self, args):
        """
        Constructor for class to create a new DB table from metadata of a FITS catalog file.
        """
        super().__init__(args)


    #
    # Methods overriding ITask interface methods
    #

    def output_results (self, metadata):
        """
        Store the given data into the configured database OR just output SQL
        to do so, depending on the 'sql-only' flag.
        """
        if (self._DEBUG):
            print("({}.output_results): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # check table name to see if it is still available in the database
        table_name = self.args.get('table_name')
        if (not self.check_table_name):
            errMsg = "Table name '{}' is not valid or already exists.".format(table_name)
            raise errors.ProcessingError(errMsg)

        # file information is needed by the SQL generation methods below
        file_info = md_utils.get_file_info(metadata)

        # Create or output the database table as a side-effect while passing metadata through.
        # Decide whether we are creating a table in the DB or just outputting SQL statements.
        sql_only = self.args.get('sql_only')
        if (sql_only):                      # if just outputting SQL
            self.write_table(table_name, metadata, file_info)
        else:                               # else storing data in a database
            self.create_table(table_name, metadata, file_info)


    #
    # Non-interface and/or task-specific Methods
    #

    def check_table_name (self, table_name):
        """
        Return True if the given table name is valid and does not already exist
        in the database, else False.
        """
        if (table_name is not None):        # TODO: IMPLEMENT LATER
            return True
        else:
            return False


    def create_table (self, table_name, metadata, file_info):
        if (self._DEBUG):
            print("({}): Creating table: '{}'".format(self.TOOL_NAME, table_name), file=sys.stderr)

        # load the database configuration from a given or default file path
        dbconfig_file = self.args.get('dbconfig_file') or DEFAULT_DBCONFIG_FILEPATH
        dbconfig = self.load_db_configuration(dbconfig_file)
        if (not dbconfig):
            errMsg = 'DB storage specified but no database configuration parameters found.'
            raise errors.ProcessingError(errMsg)

        db_uri = dbconfig.get('db_uri')
        if (not db_uri):
            errMsg = 'DB storage specified but no database URI (db_uri) parameter found.'
            raise errors.ProcessingError(errMsg)

        # open database connection and create the specified table
        db_connection = psycopg2.connect(db_uri)
        # self.create_db_table(outdata, table_name, db_connection)  # TODO: IMPLEMENT LATER
        db_connection.close()

        if (self._VERBOSE):
            print("({}): Database table '{}' created.".format(self.TOOL_NAME, table_name), file=sys.stderr)


    def write_SQL (self, table_name, metadata, file_info, file_path=None):
        """
        Generate SQL commands to insert the given data dictionary into the database,
        using the given file information dictionary. Write the SQL command strings to
        the given file path or to standard output, if no file path given.
        """
        if ((file_path is None) or (file_path == sys.stdout)):  # if writing to standard output
            sys.stdout.write(self.make_file_info_comment(file_info))
            sys.stdout.write('\n')
            # sys.stdout.write(self.make_sql_insert_string(metadata, table_name))
            sys.stdout.write('\n')

        else:                               # else file path was given
            with open(file_path, 'w') as outfile:
                outfile.write(self.make_file_info_comment(file_info))
                outfile.write('\n')
                # outfile.write(self.make_sql_insert_string(metadata, table_name))
                outfile.write('\n')


    def write_table (self, table_name, metadata, file_info):
        """ Generate and output SQL to create a new catalog table. """
        if (self._DEBUG):
            print("({}.write_table): '{}'".format(self.TOOL_NAME, table_name), file=sys.stderr)

        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')
        if (genfile):                       # if generating the output filename/path
            fname = file_info.get('file_name') if file_info else "NO_FILENAME"
            outfile = self.gen_output_file_path(fname, SQL_EXTENSION, self.TOOL_NAME)
            self.write_SQL(metadata, table_name, file_info, outfile)
        elif (outfile is not None):         # else if using the given filepath
            self.write_SQL(metadata, table_name, file_info, outfile)
        else:                               # else using standard output
            self.write_SQL(metadata, table_name, file_info)

        if (self._VERBOSE):
            out_dest = outfile if (outfile) else STDOUT_NAME
            print("({}): SQL output to '{}'".format(self.TOOL_NAME, out_dest), file=sys.stderr)
