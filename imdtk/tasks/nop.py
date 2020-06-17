#
# Class to pass through the input to the output unchanged.
#   Written by: Tom Hicks. 6/17/2020.
#   Last Modified: Initial creation.
#
from imdtk.tasks.i_task import IImdTask

class NopTask (IImdTask):
    """ Class to pass through the input to the output unchanged. """

    def __init__(self, args):
        """
        Constructor for class to pass through the input to the output unchanged.
        """
        super().__init__(args)
