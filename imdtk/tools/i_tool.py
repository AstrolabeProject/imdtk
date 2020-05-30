#
# Abstract class defining the interface for tool components.
#   Written by: Tom Hicks. 5/27/2020.
#   Last Modified: Update to work directory. Add tool name arg to output filename. Add output extents constant.
#
import abc
import datetime

from config.settings import WORK_DIR
import imdtk.core.file_utils as file_utils


OUTPUT_EXTENTS = [ '.json', '.pickle' ]


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



    def gen_output_file_path (self, file_path, extension, tool_name='', out_dir=WORK_DIR):
        """
        Return a unique output filepath, within the specified output directory,
        for the result file. Use the given file_path string and extension to create the name.
        """
        time_now = datetime.datetime.now()
        now_str = time_now.strftime("%Y%m%d_%H%M%S-%f")
        fname = file_utils.filename_core(file_path)
        tname = '_'+tool_name if tool_name else ''
        return "{0}/{1}{2}_{3}.{4}".format(out_dir, fname, tname, now_str, extension)
