#
# Class defining interface methods to store incoming data to an SQL database.
#   Written by: Tom Hicks. 6/21/2020.
#   Last Modified: Refactor method to output commented line of SQL here. Rename SQL comment method.
#
import configparser
import sys

import imdtk.exceptions as errors
from imdtk.tasks.i_task import IImdTask


# suffix for SQL output files
SQL_EXTENSION = 'sql'


class ISQLSink (IImdTask):
    """
    Class defining interface methods to store incoming data to an SQL database.
    """

    # Value which identifies records which are public: 0 means is_public = false
    IS_PUBLIC_VALUE = 0

    # String which defines a comment line in the SQL output.
    SQL_COMMENT = '--'


    def __init__(self, args):
        """
        Constructor for class defining interface methods to store incoming data to an SQL database.
        """
        super().__init__(args)


    #
    # Non-interface and/or sink-specific Methods
    #

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


    def load_sql_db_config (self, dbconfig_file):
        """
        Load the database configuration from the given filepath. Returns a dictionary
        of database configuration parameters.
        """
        if (self._DEBUG):
            print("({}): Reading DB configuration file '{}'".format(self.TOOL_NAME, dbconfig_file), file=sys.stderr)

        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(),
                                           strict=False, empty_lines_in_values=False)
        config.read(dbconfig_file)
        dbconfig = dict(config['db_properties'])

        if (not dbconfig):
            errMsg = 'DB storage specified but no database configuration parameters found.'
            raise errors.ProcessingError(errMsg)

        if (dbconfig.get('db_uri') is None):
            errMsg = 'DB storage specified but no database URI (db_uri) parameter found.'
            raise errors.ProcessingError(errMsg)

        if (self._DEBUG):
            print("({}): Read {} DB configuration properties.".format(self.TOOL_NAME, len(dbconfig)), file=sys.stderr)

        return dbconfig


    def output_SQL (self, sql_str, comment=None, file_path=None):
        """
        Output the given SQL string, and optional leading comment, to the given file path or
        to standard output, if no file path given.

        Note: the given SQL strings are assumed to be valid and safe and are not vetted.
        """
        if ((file_path is None) or (file_path == sys.stdout)):  # if writing to standard output
            if (comment is not None):
                sys.stdout.write(comment)
                sys.stdout.write('\n')
            sys.stdout.write(sql_str)
            sys.stdout.write('\n')

        else:                               # else file path was given
            with open(file_path, 'w') as outfile:
                if (comment is not None):
                    outfile.write(comment)
                    outfile.write('\n')
                outfile.write(sql_str)
                outfile.write('\n')


    def sql_file_info_comment_str (self, file_info):
        """
        Return an SQL comment string containing information about the input file.
        """
        fname = file_info.get('file_name') if file_info else "NO_FILENAME"
        fsize = file_info.get('file_size') if file_info else 0
        fpath = file_info.get('file_path') if file_info else None
        return self.file_info_to_comment_string(fname, fsize, fpath)
