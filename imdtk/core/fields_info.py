#
# Class implementing the data structure to hold information about multiple fields,
# keyed by the field name.
#   Written by: Tom Hicks. 4/11/20.
#   Last Modified: Remove leftover debug statement.
#
import os
import logging as log
from collections import UserDict


class FieldsInfo (UserDict):
    """
    Class implementing the data structure to hold information about multiple fields,
    each keyed by the field name.
    NB: The methods in this module merely augment the available dictionary methods,
        mostly to manage the special "value" property within each field.
    """

    def __init__(self, dict=None):
        self.data = {}
        if dict is not None:
            self.update(dict)


    def copy_value (self, from_key, to_key, overwrite=True):
        """
        Copy the current value from the named field to the other named field but only if
        the "From" field exists and has a value and the "To" field information already exists.
        Whether the existing "To" value is overwritten is determined by the value of the
        overwrite field (default True).
        """
        to_fld = self.data.get(to_key)                # get To FieldInfo
        from_fld = self.data.get(from_key)            # get From FieldInfo
        if (from_fld and to_fld and from_fld.has_value()): # both exist and From has a value
            if (overwrite or (not to_fld.has_value())): # dont replace value if overwrite is false
                to_fld.set_value(from_fld.get_value())


    def get_value_for (self, field_name):
        """ Return the current value for the named field, or None if the named field is
            not present or if it does not have a current value. """
        field_info = self.data.get(field_name)
        if (field_info is not None):
            return field_info.get_value()
        else:
            return None


    def has_value_for (self, field_name):
        """ Return True if the named field is present and has a data value, else False. """
        field_info = self.data.get(field_name)
        return (field_info is not None) and field_info.has_value()


    def set_value_for (self, field_name, val):
        """
        Set the value of the *existing* named field to the given value.
        NB: If the name field does not exist this function does nothing!
        """
        field_info = self.data.get(field_name)
        if (field_info is not None):
            field_info.set_value(val)
