#
# Utilities to the various metadata components in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/13/2020.
#   Last Modified: Add some getters for the catalog metadata structure.
#

# Getters for the Image Metadata structure
#
def get_aliased (metadata):
    """ Accessor for the aliased dictionary embedded in the given metadata structure. """
    return metadata.get('aliased')


def get_calculated (metadata):
    """ Accessor for the calculated dictionary embedded in the given metadata structure. """
    return metadata.get('calculated')


def get_defaults (metadata):
    """ Accessor for the defaults dictionary embedded in the given metadata structure. """
    return metadata.get('defaults')


def get_fields_info (metadata):
    """ Accessor for the fields_info dictionary embedded in the given metadata structure. """
    return metadata.get('fields_info')


def get_file_info (metadata):
    """ Accessor for the file_info dictionary embedded in the given metadata structure. """
    return metadata.get('file_info')


def get_headers (metadata):
    """ Accessor for the headers dictionary embedded in the given metadata structure. """
    return metadata.get('headers')


# Getters for the Catalog Metadata structure
#
def get_column_names (metadata):
    """ Accessor for the name array embedded in the given catalog metadata structure. """
    return metadata.get('column_info').get('name')


def get_column_formats (metadata):
    """ Accessor for the name array embedded in the given catalog metadata structure. """
    return metadata.get('column_info').get('format')
