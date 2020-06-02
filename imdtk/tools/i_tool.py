#
# Abstract class defining the interface for tool components.
#   Written by: Tom Hicks. 5/27/2020.
#   Last Modified: Move methods to output JSON and pickle here. Add name strings for standard file descriptors.
#
import abc
import datetime
import json
import pickle
import sys

from config.settings import WORK_DIR
import imdtk.core.file_utils as file_utils


OUTPUT_EXTENTS = [ '.json', '.pickle' ]

STDIN_NAME = 'standard input'
STDERR_NAME = 'standard error'
STDOUT_NAME = 'standard output'


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


    def output_JSON (self, data, file_path=None):
        """ Jsonify and write the given data structure to the given file path or standard output. """
        if (file_path is not None):         # if output file specified
            outfile = open(file_path, 'w')
            json.dump(data, outfile, indent=2)
            outfile.write('\n')
            outfile.close()
        else:                               # else write to standard output
            json.dump(data, sys.stdout, indent=2)
            sys.stdout.write('\n')


    def output_pickle (self, data, file_path=None):
        """ Pickle and write the given data structure to the given file path or standard output. """
        if (file_path is not None):         # if output file specified
            outfile = open(file_path, 'wb')
            pickle.dump(data, outfile)
            outfile.close()
        else:                               # else write to standard output
            pickle.dump(data, sys.stdout.buffer)
