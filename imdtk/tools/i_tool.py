#
# Abstract class defining the interface for tool components.
#   Written by: Tom Hicks. 5/27/2020.
#   Last Modified: Initial creation.
#
import abc

class IImdTool (abc.ABC):

    @abc.abstractmethod
    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for the instance. """
        pass


    @abc.abstractmethod
    def output_results (self, results):
        """ Output the given results in the selected format. """
        pass


    @abc.abstractmethod
    def process_and_output (self):
        """ Perform the main work of the tool and output the results in the selected format. """
        pass


    @abc.abstractmethod
    def process (self):
        """ Perform the main work of the tool and return the results as a Python structure. """
        pass
