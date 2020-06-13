#
# Abstract class defining the interface for tool components.
#   Written by: Tom Hicks. 5/27/2020.
#   Last Modified: Rename this as task.
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

OUTPUT_EXTENTS = [ '.json' ]

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


    def input_JSON (self, input_file=None, input_format=DEFAULT_INPUT_FORMAT, tool_name=''):
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
                errMsg = "({}.process): Invalid input format '{}'.".format(tool_name, input_format)
                log.error(errMsg)
                raise ValueError(errMsg)

        except Exception as ex:
            errMsg = "({}.process): Exception while reading metadata from file '{}': {}.".format(tool_name, input_file, ex)
            log.error(errMsg)
            raise RuntimeError(errMsg)

        return metadata                     # return the results of processing


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
