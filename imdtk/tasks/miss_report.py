#
# Class to report on the presence of missing fields in the FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/13/2020.
#   Last Modified: Make no report unless verbose flag set.
#
import os
import sys
import configparser
import logging as log

import imdtk.tasks.metadata_utils as md_utils
from imdtk.tasks.i_task import IImdTask


class MissingFieldsTask (IImdTask):
    """ Class which reports on missing fields in a metadata structure. """

    def __init__(self, args):
        """
        Constructor for class which reports on missing fields in a metadata structure.
        """
        super().__init__(args)


    #
    # Concrete methods implementing ITask abstract methods
    #

    def process (self, metadata):
        """
        Perform the main work of the task on the given metadata and return the results
        as a Python data structure.
        """
        if (self._DEBUG):
            print("({}.process): ARGS={}".format(self.TOOL_NAME, self.args), file=sys.stderr)

        # Create and output the report as a side-effect while passing metadata through
        # BUT be silent (act like a NO-OP) if the verbose flag is not set.
        if (self._VERBOSE):
            report = self.check_missing(metadata)  # check for missing fields
            self.output_report(report)             # output the report strings

        return metadata                     # return metadata unchanged


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
