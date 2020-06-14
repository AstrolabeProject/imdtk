#
# Abstract class defining the interface for task components.
#   Written by: Tom Hicks. 5/27/2020.
#   Last Modified: Redo output JSON to take std files. Remove unused output extents.
#
import abc
import datetime
import json
import logging as log
import sys

from config.settings import WORK_DIR
import imdtk.core.file_utils as file_utils


DEFAULT_INPUT_FORMAT = 'json'
DEFAULT_OUTPUT_FORMAT = 'json'

STDIN_NAME = 'standard input'
STDERR_NAME = 'standard error'
STDOUT_NAME = 'standard output'


class IImdTask (abc.ABC):

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
        """ Perform the main work of the task and output the results in the selected format. """
        pass


    @abc.abstractmethod
    def process (self):
        """ Perform the main work of the task and return the results as a Python structure. """
        pass



    def gen_output_file_path (self, file_path, extension, task_name='', out_dir=WORK_DIR):
        """
        Return a unique output filepath, within the specified output directory,
        for the result file. Use the given file_path string and extension to create the name.
        """
        time_now = datetime.datetime.now()
        now_str = time_now.strftime("%Y%m%d_%H%M%S-%f")
        fname = file_utils.filename_core(file_path)
        tname = '_'+task_name if task_name else ''
        return "{0}/{1}{2}_{3}.{4}".format(out_dir, fname, tname, now_str, extension)


    def input_JSON (self, input_file=None, input_format=DEFAULT_INPUT_FORMAT, task_name=''):
        """
        Process the given input file, assumed to be already validated! If the input file
        is not given, read from standard input.
        """
        try:
            if (input_format == 'json'):
                if (input_file is None):
                    metadata = json.load(sys.stdin)
                else:
                    with open(input_file) as infile:
                        metadata = json.load(infile)
            else:
                errMsg = "({}.process): Invalid input format '{}'.".format(task_name, input_format)
                log.error(errMsg)
                raise ValueError(errMsg)

        except Exception as ex:
            errMsg = "({}.process): Exception while reading metadata from file '{}': {}.".format(task_name, input_file, ex)
            log.error(errMsg)
            raise RuntimeError(errMsg)

        return metadata                     # return the results of processing


    def output_JSON (self, data, file_path=None):
        """
        Jsonify and write the given data structure to the given file path,
        standard output, or standard error.
        """
        if ((file_path is None) or (file_path == sys.stdout)): # if writing to standard output
            json.dump(data, sys.stdout, indent=2)
            sys.stdout.write('\n')

        elif (file_path == sys.stderr):     # else if writing to standard error
            json.dump(data, sys.stderr, indent=2)
            sys.stderr.write('\n')

        else:                               # else file path was given
            outfile = open(file_path, 'w')
            json.dump(data, outfile, indent=2)
            outfile.write('\n')
            outfile.close()
