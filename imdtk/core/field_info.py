#
# Facade class to hold information about a single field.
#   Written by: Tom Hicks. 4/11/20.
#   Last Modified: Add optional value argument on constructor.
#
import os
import logging as log
from collections import UserDict


class FieldInfo (UserDict):
    """
    Facade class for information about a single field.
    NB: The methods in this module merely augment the available dictionary methods to
        manage the special "value" property for the field.
    """

    # The key which identifies the value within the field information.
    _VALUE = '_value'

    def __init__(self, dict=None, value=None):
        """ Constructor taking set of initial dictionary values and/or a value for
            the special "value" property. """
        self.data = {}
        if dict is not None:
            self.update(dict)
        if (value is not None):
            self.set_value(value)


    def get_value (self):
        """ Return the current value for the "value" field, or None if the "value" field is
            not present or if it does not have a current value. """
        return self.data.get(self._VALUE)


    def has_value (self):
        """ Return True if the this field info has a data value, else return False. """
        return (self.data.get(self._VALUE) is not None)


    def set_value (self, val):
        """ Set the current value for this field to the given value (which could be None). """
        self.data[self._VALUE] = val
