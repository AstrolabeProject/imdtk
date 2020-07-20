#
# User defined exceptions for the ImdTk system.
#   Written by: Tom Hicks. 7/19/2020.
#   Last Modified: Initial creation.
#
class ProcessingError (Exception):
    """
    Base class for exceptions in this module.

    Attributes:
        message -- explanation of the error
        error_code -- integer identifying the error
    """
    ERROR_CODE = 500

    def __init__(self, message, error_code=ERROR_CODE):
        Exception.__init__(self)
        self.message = message
        if error_code is not None:
            self.error_code = error_code


    def __str__(self):
        return("({}) {}".format(self.error_code, self.message))


    def to_dict(self):
        retdict = dict()
        retdict['error_code'] = self.error_code
        retdict['message'] = self.message
        return retdict


    def to_tuple(self):
        return (self.message, self.error_code)



class UnsupportedTypeError (ProcessingError):
    """
    Class for exceptions caused by unsupported file or media types.
    """
    ERROR_CODE = 415

    def __init__(self, message, error_code=ERROR_CODE):
        super().__init__(message, error_code)
