#
# Module with utilities to add aliases (fields) for existing fields in a metadata structure.
#   Written by: Tom Hicks. 8/6/2020.
#   Last Modified: Initial creation as module.
#
import configparser
import sys

from imdtk.core.misc_utils import keep


def keep_aliased_fields (aliases, fields):
    """
    Copy each field whose key is in the aliases dictionary, replacing the field with the alias value.
    """
    return keep(aliases.get, fields)


def copy_aliased_headers (aliases, headers):
    """
    Copy each header card whose key is in aliases, replacing the header key with the alias.
    """
    copied = dict()
    if (headers is not None):
        for hdr_key, hdr_val in headers.items():
            a_key = aliases.get(hdr_key)
            if (a_key is not None):
                copied[a_key] = hdr_val
    return copied


def load_aliases (alias_file, debug=False, tool_name=''):
    """ Load field name aliases from the given alias filepath. """
    if (debug):
        print("({}): Loading from aliases file '{}'".format(tool_name, alias_file), file=sys.stderr)

    config = configparser.ConfigParser(strict=False, empty_lines_in_values=False)
    config.optionxform = lambda option: option
    config.read(alias_file)
    aliases = config['aliases']

    if (debug):
        print("({}): Read {} field name aliases.".format(tool_name, len(aliases)), file=sys.stderr)

    return dict(aliases)