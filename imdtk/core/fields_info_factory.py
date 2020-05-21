#
# Factory class to generate instances of FieldsInfo.
#   Written by: Tom Hicks. 4/9/20.
#   Last Modified: Make the no default value constant exportable from this module.
#
import os
import logging as log

from imdtk.core.field_info import FieldInfo
from imdtk.core.fields_info import FieldsInfo


# String which marks a field with "no default value" or a value to be calculated.
NO_DEFAULT_VALUE = '*'


class FieldsInfoFactory ():
    """ Factory class to generate instances of FieldsInfo. """

    # String which defines a comment line in the JWST resource files.
    COMMENT_MARKER = '#'

    # String which defines the line containing column_names in the JWST resource files.
    COLUMN_NAME_MARKER = '_COLUMN_NAMES_'

    # List of column names in the header field information file (with default values).
    DEFAULT_FIELD_INFO_COLUMN_NAMES = [ 'obsCoreKey', 'datatype', 'required', 'default' ]


    def __init__(self, args):
        """ Constructor for the JWST-specific FITS file processor class. """

        # Configuration parameters given to this class.
        self._args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = self._args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = self._args.get('debug', False)

        # List of column names in the header field information file (with default values).
        self._field_info_column_names = self._args.get('field_info_column_names') or self.DEFAULT_FIELD_INFO_COLUMN_NAMES

        # load the fields information from a given file path or a default resource path
        self._fields_file = self._args.get('fields_file')
        if (not self._fields_file):
            errMsg = "(FieldsInfoFactory.ctor): Fields Info filepath 'fields_file' missing from constructor parameters."
            log.error(errMsg)
            raise ValueError(errMsg)


    def load_fields_info (self):
        """
        Read the file containing information about the fields processed by this program,
        and return the fields in a dictionary.
        """
        if (self._DEBUG):
            print("(fields_info_factory.load_fields_info): Loading from fields info file '{}'".format(self._fields_file))

        rec_cnt = 0                         # number of field info records processed
        fields = FieldsInfo()
        num_info_fields = len(self._field_info_column_names) # to avoid computation in loop below

        all_lines = []
        with open(self._fields_file) as ff:
            all_lines = ff.read().splitlines()

        # process the lines in the fields info file
        for line in all_lines:
            line = line.strip()
            # ignore empty lines and comment lines:
            if ((not line) or line.startswith(self.COMMENT_MARKER)):
                pass

            # else if line is a column name (aka header) line:
            elif (line.startswith(self.COLUMN_NAME_MARKER)):
                sflds = [ fld.strip() for fld in line.split(',') ]
                flds = list(filter(lambda x: x, sflds))
                if (len(flds) > 2):                          # must be at least two column names
                    self._field_info_column_names = flds[1:] # drop COLUMN_NAME_MARKER (1st field)

            else:                           # else assume line is a data line
                sflds = [ fld.strip() for fld in line.split(',') ]
                if (sflds and (len(sflds) == num_info_fields)):
                    entries = zip(self._field_info_column_names, sflds)  # make dictionary entries
                    non_empty = { key: value for (key, value) in entries if (value is not None) }
                    fields[sflds[0]] = FieldInfo(non_empty)  # store all fields keyed by first field
                    rec_cnt += 1

        if (self._DEBUG):
            print("(fields_info_factory.load_fields_info): Read {} field information records.".format(rec_cnt))

        return fields
