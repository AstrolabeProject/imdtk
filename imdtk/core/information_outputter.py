#
# Class which implements the interface for storing or outputting image metadata.
#   Written by: Tom Hicks. 4/9/2020.
#   Last Modified: Get output directory from settings.
#
import os
import logging as log
import datetime
import psycopg2

from config.settings import PROGRAM_NAME, OUTPUT_DIR
from imdtk.core.i_information_outputter import IInformationOutputter


class InformationOutputter (IInformationOutputter):
    """ Class which implements the interface for storing or outputting image metadata. """

    # String which defines a comment line in the SQL output.
    SQL_COMMENT = '--'

    # String which identifies records which are public: 0 means is_public = false
    IS_PUBLIC_VALUE = '0'


    def __init__(self, args):
        """ Constructor for the class storing or outputting image metadata. """

        # Configuration parameters given to this class.
        self._args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = args.get('debug', False)

        # An output file created within the output directory.
        self._output_file = None

        # Output format for the information when output.
        self._output_format = args.get('output_format') or 'db'

        # List of field names to skip when outputting fields.
        self._skipFieldList = []

        # Database manipulation facade class.
        self._DB_connection = None

        # Schema and table name in which to store image metadata in the database.
        self._metadata_table_name = args.get('metadata_table_name') or 'sia.jwst'

        if (self._output_format != 'db'):   # if writing to a file
            out_file_path = self.gen_output_file_path(OUTPUT_DIR)
            self._output_file = open(out_file_path, 'w')

        else:                               # else writing to a database
            db_config = args.get('db_config')
            if (not db_config):
                errMsg = 'DB storage specified but no database configuration parameters found.'
                raise RuntimeError(errMsg)
            db_uri = db_config.get('db_uri')
            if (not db_uri):
                errMsg = 'DB storage specified but no database URI ("db_uri") parameter found.'
                raise RuntimeError(errMsg)
            self._DB_connection = psycopg2.connect(db_uri)


    #
    # Concrete methods implementing IInformationOutputter abstract methods
    #

    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for the outputter instance. """
        if (self._DEBUG):
            print("(information_outputter.cleanup)")
        if (self._DB_connection is not None):
            self._DB_connection.close()
            self._DB_connection = None
        if (self._output_file is not None):
            self._output_file.close()
            self._output_file = None


    def output_image_info (self, fields_info):
        """ Output the given field information using the current output settings. """
        if (self._DEBUG):
            print("(information_outputter.output_image_info): output={}".format(self._output_format))

        if (self._output_format == 'db'):   # if writing to database
            self.store_image_info(fields_info)

        elif (self._output_format == 'sql'): # else if writing to an output file
            self._output_file.write(self.make_file_info(fields_info))
            self._output_file.write('\n')
            self._output_file.write(self.make_data_line(fields_info))
            self._output_file.write('\n')

        else:                               # LATER: handle JSON and CSV?
            pass


    def store_image_info (self, fields_info):
        """ Load the given field information directly into a database. """
        if (self._DEBUG):
            print("(information_outputter.store_image_info)")
        # using connection in a with block commits transaction but does NOT close connection
        with self._DB_connection as conn:
            with conn.cursor() as cursor:
                (fmt_str, values) = self.make_sql_for_db(fields_info)
                cursor.execute(fmt_str, values)


    #
    # Non-interface Methods
    #

    def file_info_to_string (self, file_name, file_size, file_path):
        """
        Return an output string for the current output format or None, if not appropriate.
        Should not be called when storing to a database.
        """
        if (self._output_format == 'sql'):
            buf = self.SQL_COMMENT + ' '    # generating an SQL comment line
            if (file_name is not None):
                buf += file_name + ' '
            if (file_size is not None):
                buf += str(file_size) + ' '
            if (file_path is not None):
                buf += file_path
            return buf                      # return formatted comment line

        else:                               # sanity check: output format must be valid
            return None


    def gen_output_file_path (self, out_dir):
        """ Return a unique output filepath, within the specified directory, for the result file. """
        time_now = datetime.datetime.now()
        now_str = time_now.strftime("%Y%m%d_%H%M%S-%f")
        return "{0}/{1}-{2}.{3}".format(out_dir, PROGRAM_NAME, now_str, self._output_format)


    def make_data_line (self, fields_info):
        """ Return a string which formats the given field information. """
        if (self._output_format == 'csv'):
            return self.to_CSV(fields_info)
        elif (self._output_format == 'json'):
            return self.to_JSON(fields_info)
        else:                               # make SQL string
            return self.to_SQL(fields_info)


    def make_file_info (self, fields_info):
        """ Return a string containing information about the input file, formatted as a comment. """
        fname_info = fields_info.get_value_for('file_name')
        fpath_info = fields_info.get_value_for('file_path')
        # estimated size is the size of the file:
        fsize_info = fields_info.get_value_for('access_estsize')
        return self.file_info_to_string(fname_info, fsize_info, fpath_info)


    def make_sql_for_db (self, fields_info):
        """
        Return the given field information formatted appropriately for inserting
        into a database via a database access library. Currently using Psycopg2
        so return a tuple of an INSERT template string and a sequence of values.
        """
        valued = { k:fi for k,fi in fields_info.items() if fi.has_value() }
        keys = ', '.join(valued.keys())
        values = [ fi.get_value() for fi in valued.values() if fi.has_value() ]
        place_holders = ', '.join(['%s' for v in values])
        template = "insert into {0} ({1}) values ({2});".format(self._metadata_table_name, keys, place_holders)
        return (template, values)


    def to_CSV (self, fields_info):
        """ Return the given field information formatted as a CSV string. """
        return ''                           # CSV NOT YET IMPLEMENTED


    def to_JSON (self, fields_info):
        """ Return the given field information formatted as a JSON string. """
        return '[]'                         # JSON NOT YET IMPLEMENTED


    def to_SQL (self, fields_info):
        """ Return the given field information formatted as an SQL INSERT string. """
        valued = { k:fi for k,fi in fields_info.items() if fi.has_value() }
        keys = ', '.join(valued.keys())
        vals = [ fi.get_value() for fi in valued.values() if fi.has_value() ]
        values = ', '.join([ ("'{}'".format(v) if (isinstance(v, str)) else str(v)) for v in vals ])
        return "insert into {0} ({1}) values ({2});".format(self._metadata_table_name, keys, values)
