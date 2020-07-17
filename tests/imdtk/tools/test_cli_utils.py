# Tests for the CLI utilities module.
#   Written by: Tom Hicks. 7/15/2020.
#   Last Modified: Add tests for check_*_file methods.
#
import argparse
import pytest
import os

import imdtk.cli_utils as utils
from config.settings import TEST_DIR

TOOL_NAME = 'TEST_CLI_UTILS'
VERSION = '1.0'


class TestCliUtils(object):

    nosuch_tstfyl = "/tests/resources/NOSUCHFILE"
    m13_tstfyl    = "{}/resources/m13.fits".format(TEST_DIR)
    # alias_tstfyl  = "{}/resources/aliases.yaml".format(TEST_DIR)
    # dbconf_tstfyl = "{}/resources/test-dbconfig.ini".format(TEST_DIR)
    # fields_tstfyl = "{}/resources/test-fields.txt".format(TEST_DIR)
    # text_tstfyl   = "{}/resources/mdkeys.txt".format(TEST_DIR)


    def test_add_aliases_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_aliases_arguments(parser, TOOL_NAME, VERSION)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'alias_file' not in args     # no default

        args = vars(parser.parse_args(['-a', 'aliases.ini']))
        print(args)
        assert 'alias_file' in args

        args = vars(parser.parse_args(['--aliases', '/fake/aliases.ini']))
        print(args)
        assert 'alias_file' in args


    def test_add_collection_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_collection_arguments(parser, TOOL_NAME, VERSION)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'collection' not in args     # no default

        args = vars(parser.parse_args(['-c', 'coll_name']))
        print(args)
        assert 'collection' in args

        args = vars(parser.parse_args(['--collection', 'collection_name']))
        print(args)
        assert 'collection' in args


    def test_add_database_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_database_arguments(parser, TOOL_NAME, VERSION)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'dbconfig_file' not in args  # no default
        assert 'sql_only' in args           # it has a default
        assert 'table_name' not in args     # no default

        args = vars(parser.parse_args(['-db', 'dbconfig.ini']))
        print(args)
        assert 'dbconfig_file' in args
        assert 'sql_only' in args           # it has a default
        assert 'table_name' not in args     # no default

        args = vars(parser.parse_args([
            '--db-config', '/fake/dbconfig.ini', '--table-name', 'mytable', '--sql-only']))
        print(args)
        assert 'dbconfig_file' in args
        assert 'table_name' in args
        assert 'sql_only' in args


    def test_add_fields_info_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_fields_info_arguments(parser, TOOL_NAME, VERSION)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'fields_file' not in args    # no default

        args = vars(parser.parse_args(['-fi', 'fields_file.ini']))
        print(args)
        assert 'fields_file' in args

        args = vars(parser.parse_args(['--fields-info', '/fake/fields_file.ini']))
        print(args)
        assert 'fields_file' in args


    def test_add_fits_file_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_fits_file_arguments(parser, TOOL_NAME, VERSION)

        with pytest.raises(SystemExit) as se:
            args = vars(parser.parse_args([])) # fits-file is required
        assert se.type == SystemExit

        args = vars(parser.parse_args(['-ff', 'astro.fits']))
        print(args)
        assert 'fits_file' in args
        assert 'which_hdu' in args          # it has a default

        args = vars(parser.parse_args(['--fits-file', '/fake/astro.fits', '--hdu', '1']))
        print(args)
        assert 'fits_file' in args
        assert 'which_hdu' in args


    def test_add_input_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_input_arguments(parser, TOOL_NAME, VERSION)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'input_file' not in args     # no default

        args = vars(parser.parse_args(['-if', 'metadata.json']))
        print(args)
        assert 'input_file' in args

        args = vars(parser.parse_args(['--input-file', '/fake/metadata.json']))
        print(args)
        assert 'input_file' in args


    def test_add_output_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_output_arguments(parser, TOOL_NAME, VERSION)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'output_file' not in args    # no default
        assert 'gen_file_path' in args      # it has a default

        args = vars(parser.parse_args(['-of', 'output.json']))
        print(args)
        assert 'output_file' in args
        assert 'gen_file_path' in args      # it has a default

        args = vars(parser.parse_args(['--output-file', '/fake/output.json', '--generate']))
        print(args)
        assert 'output_file' in args
        assert 'gen_file_path' in args


    def test_add_report_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_report_arguments(parser, TOOL_NAME, VERSION)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'report_format' in args      # it has a default

        args = vars(parser.parse_args(['-rfmt', 'json']))
        print(args)
        assert 'report_format' in args

        args = vars(parser.parse_args(['--report-format', 'json']))
        print(args)
        assert 'report_format' in args


    def test_add_shared_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_shared_arguments(parser, TOOL_NAME, VERSION)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'version' not in args        # no default
        assert 'debug' in args              # it has a default
        assert 'verbose' in args            # it has a default

        with pytest.raises(SystemExit) as se:
            args = vars(parser.parse_args(['--version'])) # version action exits
        assert se.type == SystemExit

        args = vars(parser.parse_args(['-v']))
        print(args)
        assert 'version' not in args        # no default
        assert 'debug' in args              # it has a default
        assert 'verbose' in args            # it has a default

        args = vars(parser.parse_args(['--verbose']))
        print(args)
        assert 'version' not in args        # no default
        assert 'debug' in args              # it has a default
        assert 'verbose' in args            # it has a default

        args = vars(parser.parse_args(['-d']))
        print(args)
        assert 'version' not in args        # no default
        assert 'debug' in args              # it has a default
        assert 'verbose' in args            # it has a default

        args = vars(parser.parse_args(['--debug']))
        print(args)
        assert 'version' not in args        # no default
        assert 'debug' in args              # it has a default
        assert 'verbose' in args            # it has a default


    def test_check_alias_file(self):
        with pytest.raises(SystemExit) as se:
            utils.check_alias_file(self.nosuch_tstfyl, TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == 30


    def test_check_dbconfig_file(self):
        with pytest.raises(SystemExit) as se:
            utils.check_dbconfig_file(self.nosuch_tstfyl, TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == 31


    def test_check_fields_file(self):
        with pytest.raises(SystemExit) as se:
            utils.check_fields_file(self.nosuch_tstfyl, TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == 32


    def test_check_fits_file_bad(self):
        with pytest.raises(SystemExit) as se:
            utils.check_fits_file(self.nosuch_tstfyl, TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == 21


    def test_check_fits_file(self):
        try:
            utils.check_fits_file(self.m13_tstfyl, TOOL_NAME)
        except SystemExit as se:
            pytest.fail("test_cli_utils.test_check_fits_file: unexpected SystemExit: {}".format(repr(se)))


    def test_check_input_file(self):
        with pytest.raises(SystemExit) as se:
            utils.check_input_file(self.nosuch_tstfyl, TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == 20