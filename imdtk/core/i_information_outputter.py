#
# Abstract class defining the interface for classes which store or output image metadata.
#   Written by: Tom Hicks. 4/9/2020.
#   Last Modified: Alphabetize order of abstract methods.
#
import abc

class IInformationOutputter (abc.ABC):

    # The special keyword for input file information in the field information map. */
    FILE_INFO_KEYWORD = '_FILE_INFO_'


    @abc.abstractmethod
    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for the instance. """
        pass


    @abc.abstractmethod
    def output_image_info (fields_info):
        """ Output the given field information using the current output settings. """
        pass


    @abc.abstractmethod
    def store_image_info (fields_info):
        """ Load the given field information directly into a database. """
        pass
