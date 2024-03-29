#
# Abstract class defining the interface for task components.
#   Written by: Tom Hicks. 5/27/2020.
#   Last Modified: Add JSON keywords to output_JSON.
#
import datetime
import json
import sys

from config.settings import WORK_DIR
import imdtk.exceptions as errors
import imdtk.core.file_utils as file_utils
import imdtk.tasks.metadata_utils as md_utils


DEFAULT_INPUT_FORMAT = 'json'
DEFAULT_OUTPUT_FORMAT = 'json'

STDIN_NAME = 'standard input'
STDERR_NAME = 'standard error'
STDOUT_NAME = 'standard output'


class IImdTask ():

    def __init__(self, args):
        """
        Constructor to initialize this parent of every child task.
        """

        # Display name of this task
        self.TOOL_NAME = args.get('TOOL_NAME') or 'unnamed_tool'

        # Configuration parameters given to this class.
        self.args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = args.get('debug', False)


    #
    # Top-level IPO methods - can be overridden by any child task, as needed
    #

    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for the task instance. """
        if (self._DEBUG):
            print("({}.cleanup)".format(self.TOOL_NAME), file=sys.stderr)


    def input_data (self):
        """
        Read data from a file or stream and return it as a Python data structure.
        """
        if (self._DEBUG):
            print("({}.input_data): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # process the given, already validated input file
        input_file = self.args.get('input_file')
        if (self._VERBOSE):
            if (input_file is None):
                print("({}): Reading data from {}".format(self.TOOL_NAME, STDIN_NAME), file=sys.stderr)
            else:
                print("({}): Reading data file '{}'".format(self.TOOL_NAME, input_file), file=sys.stderr)

        input_format = self.args.get('input_format') or DEFAULT_INPUT_FORMAT
        if (input_format == 'json'):
            data = self.input_JSON(input_file)
        else:                               # currently, no other input formats
            errMsg = "({}.process): Invalid input format '{}'.".format(self.TOOL_NAME, input_format)
            raise errors.ProcessingError(errMsg)

        return data                         # return the input data


    def input_and_process (self):
        """
        Read input data, perform the main work of the task, and return the results
        as a Python data structure.
        """
        return self.process(self.input_data())


    def input_process_output (self):
        """
        Read input data, perform the main work of the task, and output the results
        in the configured output format.
        """
        self.process_and_output(self.input_data())


    def process (self, data=None):
        """
        Perform the main work of the task, on any given data, and return the results
        as a Python data structure.

        NOTE: this default implementation is a NO-OP: it merely passes the input data
              to the output. It must be overridden to do anything useful.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        if (data):
            self.output_results(data)


    def process_and_output (self, data=None):
        """
        Perform the main work of the task, on any given data, and output the results
        in the configured output format.
        """
        data = self.process(data)
        if (data):
            self.output_results(data)


    def output_results (self, metadata):
        """ Output the given metadata in the configured output format. """
        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')
        out_fmt = self.args.get('output_format') or DEFAULT_OUTPUT_FORMAT

        if (out_fmt == 'json'):
            if (genfile):                   # if generating the output filename/path
                file_info = md_utils.get_file_info(metadata)
                fname = file_info.get('file_name') if file_info else "NO_FILENAME"
                outfile = self.gen_output_file_path(fname, out_fmt, self.TOOL_NAME)
                self.output_JSON(metadata, outfile)
            elif (outfile is not None):     # else if using the given filepath
                self.output_JSON(metadata, outfile)
            else:                           # else using standard output
                self.output_JSON(metadata)

        else:
            errMsg = "({}.process): Invalid output format '{}'.".format(self.TOOL_NAME, out_fmt)
            raise errors.ProcessingError(errMsg)

        if (self._VERBOSE):
            out_dest = outfile if (outfile) else STDOUT_NAME
            print("({}): Results output to '{}'".format(self.TOOL_NAME, out_dest), file=sys.stderr)


    #
    # Support methods - less likely to be overridden by a child task, but possible.
    #

    def gen_output_file_path (self, file_path, extension, task_name='', out_dir=WORK_DIR):
        """
        Return a unique output filepath, within the specified output directory,
        for the result file. Use the given file_path string and extension to create the name.
        """
        time_now = datetime.datetime.now()
        now_str = time_now.strftime("%Y%m%d_%H%M%S-%f")
        fname = file_utils.filename_core(file_path)
        tname = '_' + task_name if task_name else ''
        return "{0}/{1}{2}_{3}.{4}".format(out_dir, fname, tname, now_str, extension)


    def input_JSON (self, input_file=None):
        """
        Process the given input file, assumed to be already validated! If the input file
        is not given, read from standard input.
        """
        if (input_file is None):
            metadata = json.load(sys.stdin)
        else:
            with open(input_file) as infile:
                metadata = json.load(infile)

        return metadata                     # return the results of processing


    def output_JSON (self, data, file_path=None, **json_keywords):
        """
        Jsonify and write the given data structure to the given file path,
        standard output, or standard error.
        """
        if ((file_path is None) or (file_path == sys.stdout)):  # if writing to standard output
            json.dump(data, sys.stdout, indent=2, **json_keywords)
            sys.stdout.write('\n')

        elif (file_path == sys.stderr):     # else if writing to standard error
            json.dump(data, sys.stderr, indent=2, **json_keywords)
            sys.stderr.write('\n')

        else:                               # else file path was given
            outfile = open(file_path, 'w')
            json.dump(data, outfile, indent=2, **json_keywords)
            outfile.write('\n')
            outfile.close()
