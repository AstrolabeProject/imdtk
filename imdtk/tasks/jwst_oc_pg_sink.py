#
# Class to sink incoming ObsCore metadata to a PostgreSQL database.
#   Written by: Tom Hicks. 6/21/2020.
#   Last Modified: Add SQL output logic, DB store infrastructure but no DB store yet.
#
import os
import sys
import logging as log

import imdtk.core.misc_utils as misc_utils
import imdtk.tasks.metadata_utils as md_utils
from config.settings import DEFAULT_DBCONFIG_FILEPATH, DEFAULT_METADATA_TABLE_NAME
from imdtk.tasks.i_task import STDOUT_NAME
from imdtk.tasks.i_oc_sql_sink import IObsCoreSQLSink, SQL_EXTENT


class JWST_ObsCorePostgreSQLSink (IObsCoreSQLSink):
    """ Class to sink incoming ObsCore metadata to a PostgreSQL database. """

    # List of column names to skip when outputting column values.
    skipColumnList = [ 'file_size' ]


    def __init__(self, args):
        """
        Constructor for class to sink incoming ObsCore metadata to a PostgreSQL database.
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

        # decide whether we are storing data in the DB or just outputting SQL statements
        sql_only = self.args.get('sql_only')
        if (sql_only):                      # if just outputting SQL
            self.output_results(metadata)
        else:                               # else storing data in a database
            self.store_results(metadata)


    #
    # Non-interface and/or task-specific Methods
    #

    def load_db_config (self, dbconfig_file):
        """ Load the database configuration from the given filepath. """
        if (self._VERBOSE):
            print("({}): Reading DB configuration file '{}'".format(self.TOOL_NAME, dbconfig_file), file=sys.stderr)

        dbconfig = self.load_db_configuration(dbconfig_file)

        if (self._VERBOSE):
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


    def make_data_line (self, metadata):
        table_name = self.args.get('table_name') or DEFAULT_METADATA_TABLE_NAME
        calculated = md_utils.get_calculated(metadata)
        misc_utils.remove_entries(calculated, ignore=self.skipColumnList)
        return self.to_SQL(calculated, table_name)


    def make_file_info_comment (self, metadata):
        """ Return a string containing information about the input file, formatted as a comment. """
        file_info = md_utils.get_file_info(metadata)
        fname = file_info.get('file_name') if file_info else "NO_FILENAME"
        fsize = file_info.get('file_size') if file_info else 0
        fpath = file_info.get('file_path') if file_info else None
        return self.file_info_to_comment_string(fname, fsize, fpath)


    def output_results (self, metadata):
        """ Generate and output SQL to save the given metadata. """
        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')
        if (genfile):                       # if generating the output filename/path
            file_info = md_utils.get_file_info(metadata)
            fname = file_info.get('file_name') if file_info else "NO_FILENAME"
            outfile = self.gen_output_file_path(fname, SQL_EXTENT, self.TOOL_NAME)
            self.output_SQL(metadata, outfile)
        elif (outfile is not None):         # else if using the given filepath
            self.output_SQL(metadata, outfile)
        else:                               # else using standard output
            self.output_SQL(metadata)

        if (self._VERBOSE):
            out_dest = outfile if (outfile) else STDOUT_NAME
            print("({}): Results output to '{}'".format(self.TOOL_NAME, out_dest), file=sys.stderr)


    def output_SQL (self, metadata, file_path=None):
        """
        Create SQL to store the given data structure and write it to the given file path,
        standard output, or standard error.
        """
        if ((file_path is None) or (file_path == sys.stdout)): # if writing to standard output
            sys.stdout.write(self.make_file_info_comment(metadata))
            sys.stdout.write('\n')
            sys.stdout.write(self.make_data_line(metadata))
            sys.stdout.write('\n')

        else:                               # else file path was given
            with open(file_path, 'w') as outfile:
                outfile.write(self.make_file_info_comment(metadata))
                outfile.write('\n')
                outfile.write(self.make_data_line(metadata))
                outfile.write('\n')


    def store_results (self, metadata):
        # load the database configuration from a given or default file path
        table_name = self.args.get('table_name') or DEFAULT_METADATA_TABLE_NAME

        dbconfig_file = self.args.get('dbconfig_file') or DEFAULT_DBCONFIG_FILEPATH
        dbconfig = self.load_db_config(dbconfig_file)
        if (not dbconfig):
            errMsg = "({}.store_results): DB storage specified but no database configuration parameters found.".format(self.TOOL_NAME)
            log.error(errMsg)
            raise RuntimeError(errMsg)

        db_uri = dbconfig.get('db_uri')
        if (not db_uri):
            errMsg = "({}.store_results): DB storage specified but no database URI (db_uri) parameter found.".format(self.TOOL_NAME)
            log.error(errMsg)
            raise RuntimeError(errMsg)

        # TODO: IMPLEMENT DB store LATER:
        # self._DB_connection = psycopg2.connect(db_uri)    


    def to_SQL (self, adict, table_name):
        """ Return the given dictionary formatted as an SQL INSERT string. """
        keys = ', '.join(adict.keys())
        vals = adict.values()
        values = ', '.join([ ("'{}'".format(v) if (isinstance(v, str)) else str(v)) for v in vals ])
        return "insert into {0} ({1}) values ({2});".format(table_name, keys, values)
