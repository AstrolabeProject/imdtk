#
# Class to report on the presence of missing fields in the FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/13/2020.
#   Last Modified: Update for super init.
#
import os, sys
import configparser
import json
import logging as log

from config.settings import CONFIG_DIR
from imdtk.tasks.i_task import IImdTask, STDIN_NAME, STDOUT_NAME
import imdtk.tasks.metadata_utils as md_utils


class MissingFieldsTask (IImdTask):
    """ Class which reports on missing fields in a metadata structure. """

    def __init__(self, args):
        """
        Constructor for class which reports on missing fields in a metadata structure.
        """
        super().__init__(args)              # call parent init


    #
    # Concrete methods implementing ITask abstract methods
    #

    def process (self):
        """
        Perform the main work of the task and return the results as a Python structure.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # process the given, already validated input file
        input_file = self.args.get('input_file')
        if (self._VERBOSE):
            if (input_file is None):
                print("({}): Reading metadata from {}".format(self.TOOL_NAME, STDIN_NAME), file=sys.stderr)
            else:
                print("({}): Reading metadata file '{}'".format(self.TOOL_NAME, input_file), file=sys.stderr)

        # read metadata from the input file in the specified input format
        input_format = self.args.get('input_format') or DEFAULT_INPUT_FORMAT
        metadata = self.input_JSON(input_file, input_format, self.TOOL_NAME)

        # create and output the report as a side-effect while passing metadata through
        report = self.check_missing(metadata) # check for missing fields

        self.output_report(report)          # output the report strings

        return metadata                     # return metadata unchanged


    def output_results (self, metadata):
        """ Output the given metadata in the selected format. """
        genfile = self.args.get('gen_file_path')
        outfile = self.args.get('output_file')
        out_fmt = self.args.get('output_format') or 'json'

        if (out_fmt == 'json'):
            if (genfile):                   # if generating the output filename/path
                file_info = md_utils.get_file_info(metadata)
                fname = file_info.get('file_name') if file_info else "NO_FILENAME"
                outfile = self.gen_output_file_path(fname, out_fmt, self.TOOL_NAME)
                self.output_JSON(metadata, outfile)
            elif (outfile is not None):     # else if using the given filepath
                self.output_JSON(metadata, outfile)
            else:                           # else using standard output
                self.output_JSON(metadata, sys.stdout)

        else:
            errMsg = "({}.process): Invalid output format '{}'.".format(self.TOOL_NAME, out_fmt)
            log.error(errMsg)
            raise ValueError(errMsg)

        if (self._VERBOSE):
            out_dest = outfile if (outfile) else STDOUT_NAME
            print("({}): Results output to '{}'".format(self.TOOL_NAME, out_dest), file=sys.stderr)


    #
    # Non-interface and/or task-specific Methods
    #

    def check_missing (self, metadata):
        """
        Check for missing fields in the results part of the given metadata.
        Returns a list of warning message strings, to be later formatted and output.
        """
        report = []
        calculated = md_utils.get_calculated(metadata)

        fields_info = md_utils.get_fields_info(metadata)
        for field_name, props in fields_info.items():
            if (field_name not in calculated):
                req_fld = 'Required' if props.get('required') else 'Optional'
                msg = "WARNING: {0} field '{1}' still does not have a value.".format(req_fld, field_name)
                report.append(msg)

        return report                       # return list of message strings


    def output_report (self, report):
        """ Output the given list of report strings in the selected format. """
        rpt_fmt = self.args.get('report_format') or 'text'

        if (rpt_fmt == 'json'):
            self.output_JSON(report, sys.stderr)

        elif (rpt_fmt == 'text'):
            for line in report:
                print(line, file=sys.stderr)

        else:
            errMsg = "({}.process): Invalid report format '{}'.".format(self.TOOL_NAME, rpt_fmt)
            log.error(errMsg)
            raise ValueError(errMsg)
