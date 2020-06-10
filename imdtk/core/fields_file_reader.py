#
# Module to generate instances of FieldsInfo.
#   Written by: Tom Hicks. 4/9/20.
#   Last Modified: Rewrite class as a module.
#

# String which marks a field with "no default value" or a value to be calculated.
NO_DEFAULT_VALUE = '*'

# String which defines a comment line in the JWST resource files.
COMMENT_MARKER = '#'

# String which defines the line containing column_names in the JWST resource files.
COLUMN_NAME_MARKER = '_COLUMN_NAMES_'

# List of column names in the header field information file (with default values).
DEFAULT_FIELD_INFO_COLUMN_NAMES = [ 'obsCoreKey', 'required', 'default' ]


def load (fields_file, field_info_column_names=DEFAULT_FIELD_INFO_COLUMN_NAMES):
    """
    Read the file containing information about the fields processed by this program,
    and return the fields in a dictionary.
    """
    fields = dict()                         # return dictionary of dictionaries

    num_info_fields = len(field_info_column_names)  # to avoid computation in loop below

    all_lines = []
    with open(fields_file) as ff:
        all_lines = ff.read().splitlines()

    # process the lines in the fields info file
    for line in all_lines:
        line = line.strip()

        # ignore empty lines and comment lines:
        if ((not line) or line.startswith(COMMENT_MARKER)):
            pass

        # else if line is a column name (aka header) line:
        elif (line.startswith(COLUMN_NAME_MARKER)):
            sflds = [ fld.strip() for fld in line.split(',') ]
            flds = list(filter(lambda x: x, sflds))
            if (len(flds) > 2):                     # must be at least two column names
                field_info_column_names = flds[1:]  # drop COLUMN_NAME_MARKER (1st field)
                num_info_fields = len(field_info_column_names)  # recompute: may have just changed

        # else assume line is a data line and process it
        else:
            sflds = [ fld.strip() for fld in line.split(',') ]
            if (sflds and (len(sflds) == num_info_fields)):
                entries = zip(field_info_column_names, sflds) # make dictionary entries
                fld_dict = { key: value for (key, value) in entries if (value is not None) }
                fields[sflds[0]] = fld_dict # store all fields keyed by first field

    return fields
