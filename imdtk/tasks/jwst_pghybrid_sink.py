#
# Class to sink incoming image metadata to a Hybrid (SQL/JSON) PostgreSQL database.
#   Written by: Tom Hicks. 7/3/2020.
#   Last Modified: Revamp error handling.
#
import json
import psycopg2
import sys

from config.settings import DEFAULT_DBCONFIG_FILEPATH, DEFAULT_HYBRID_TABLE_NAME
import imdtk.exceptions as errors
import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import STDOUT_NAME
from imdtk.tasks.i_sql_sink import ISQLSink, SQL_EXTENSION


class JWST_HybridPostgreSQLSink (ISQLSink):
    """ Class to sink incoming image metadata to a Hybrid PostgreSQL database. """

    # List of names of required SQL fields:
    SQL_FIELDS = [ 's_dec', 's_ra', 'obs_collection', 'is_public' ]


    def __init__(self, args):
        """
        Constructor for class to sink incoming image metadata to a Hybrid PostgreSQL database.
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

    def load_db_config (self, dbconfig_file):
        """ Load the database configuration from the given filepath. """
        if (self._DEBUG):
            print("({}): Reading DB configuration file '{}'".format(self.TOOL_NAME, dbconfig_file), file=sys.stderr)

        dbconfig = self.load_db_configuration(dbconfig_file)

        if (self._DEBUG):
            print("({}): Read {} DB configuration properties.".format(self.TOOL_NAME, len(dbconfig)), file=sys.stderr)

        return dbconfig


    def file_info_to_comment_string (self, file_name, file_size, file_path):
        """
        Return an SQL comment string containing the given file information.
        """
        buf = self.SQL_COMMENT + ' '    # generating an SQL comment line
        if (file_name is not None):
            buf += file_name + ' '
        if (file_size is not None):
            buf += str(file_size) + ' '
        if (file_path is not None):
            buf += file_path
        return buf                          # return formatted comment line


    def make_file_info_comment (self, file_info):
        """ Return a string containing information about the input file, formatted as a comment. """
        fname = file_info.get('file_name') if file_info else "NO_FILENAME"
        fsize = file_info.get('file_size') if file_info else 0
        fpath = file_info.get('file_path') if file_info else None
        return self.file_info_to_comment_string(fname, fsize, fpath)


    def make_sql_insert_db (self, datadict, table_name):
        """
        Return appropriate data structures for inserting the given data dictionary
        into a database via a database access library. Currently using Psycopg2,
        so return a tuple of an INSERT template string and a sequence of values.
        """
        fieldnames = self.SQL_FIELDS.copy()
        fieldnames.append('metadata')          # add name of the JSON metadata field
        keys = ', '.join(fieldnames)

        values = [ datadict.get(key) for key in self.SQL_FIELDS if datadict.get(key) is not None ]
        values.append(self.to_JSON(datadict))  # add the JSON for the metadata field

        place_holders = ', '.join(['%s' for v in values])
        template = "insert into {0} ({1}) values ({2});".format(table_name, keys, place_holders)
        return (template, values)


    def make_sql_insert_string (self, datadict, table_name):
        """ Return an SQL INSERT string to store the given data dictionary. """
        fieldnames = self.SQL_FIELDS.copy()
        fieldnames.append('metadata')         # add name of the JSON metadata field
        keys = ', '.join(fieldnames)

        vals = [ datadict.get(key) for key in self.SQL_FIELDS if datadict.get(key) is not None ]
        vals.append(self.to_JSON(datadict))   # add the JSON for the metadata field
        values = ', '.join([ ("'{}'".format(v) if (isinstance(v, str)) else str(v)) for v in vals ])

        return "insert into {0} ({1}) values ({2});".format(table_name, keys, values)


    def select_data_for_output (self, metadata):
        """
        Select a subset of data, from the given metadata, for output.
        Returns a single dictionary of selected data.
        """
        selected = md_utils.get_calculated(metadata).copy()
        return selected                     # return selected dataset


    def store_data (self, outdata, table_name, db_connection):
        """
        Store the given data structure directly into the given table in the connected database.
        """
        # using connection in a with block commits transaction but does NOT close connection
        with db_connection as conn:
            with conn.cursor() as cursor:
                (fmt_str, values) = self.make_sql_insert_db(outdata, table_name)
                cursor.execute(fmt_str, values)


    def store_results (self, outdata, file_info):
        """
        Store the given data dictionary into the configured database table.
        """
        if (self._DEBUG):
            print("({}.store_results)".format(self.TOOL_NAME), file=sys.stderr)

        table_name = self.args.get('table_name') or DEFAULT_HYBRID_TABLE_NAME

        # load the database configuration from a given or default file path
        dbconfig_file = self.args.get('dbconfig_file') or DEFAULT_DBCONFIG_FILEPATH
        dbconfig = self.load_db_config(dbconfig_file)
        if (not dbconfig):
            errMsg = 'DB storage specified but no database configuration parameters found.'
            raise errors.ProcessingError(errMsg)

        db_uri = dbconfig.get('db_uri')
        if (not db_uri):
            errMsg = 'DB storage specified but no database URI (db_uri) parameter found.'
            raise errors.ProcessingError(errMsg)

        # open database connection and store the data
        db_connection = psycopg2.connect(db_uri)
        self.store_data(outdata, table_name, db_connection)
        db_connection.close()

        if (self._VERBOSE):
            print("({}): Results stored in '{}'".format(self.TOOL_NAME, table_name), file=sys.stderr)


    def to_JSON (self, datadict):
        """ Create and return a JSON string corresponding to the given data dictionary. """
        return json.dumps(datadict, sort_keys=True)


    def write_results (self, outdata, file_info):
        """ Generate and output SQL to save the given data dictionary. """
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
        Generate SQL commands to insert the given data dictionary into the database,
        using the given file information dictionary. Write the SQL command strings to
        the given file path or to standard output, if no file path given.
        """
        table_name = self.args.get('table_name') or DEFAULT_HYBRID_TABLE_NAME

        if ((file_path is None) or (file_path == sys.stdout)):  # if writing to standard output
            sys.stdout.write(self.make_file_info_comment(file_info))
            sys.stdout.write('\n')
            sys.stdout.write(self.make_sql_insert_string(outdata, table_name))
            sys.stdout.write('\n')

        else:                               # else file path was given
            with open(file_path, 'w') as outfile:
                outfile.write(self.make_file_info_comment(file_info))
                outfile.write('\n')
                outfile.write(self.make_sql_insert_string(outdata, table_name))
                outfile.write('\n')
