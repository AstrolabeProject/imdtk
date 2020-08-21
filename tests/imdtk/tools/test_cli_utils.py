# Tests for the CLI utilities module.
#   Written by: Tom Hicks. 7/15/2020.
#   Last Modified: Update for CLI utils redo.
#
import argparse
import pytest

import imdtk.tools.cli_utils as utils
from tests import TEST_DIR

TOOL_NAME = 'TEST_CLI_UTILS'


class TestCliUtils(object):

    nosuch_tstfyl = "/tests/resources/NOSUCHFILE"
    m13_tstfyl    = "{}/resources/m13.fits".format(TEST_DIR)
    # alias_tstfyl  = "{}/resources/aliases.yaml".format(TEST_DIR)
    # dbconf_tstfyl = "{}/resources/test-dbconfig.ini".format(TEST_DIR)
    # text_tstfyl   = "{}/resources/mdkeys.txt".format(TEST_DIR)
    resources_tstdir = "{}/resources".format(TEST_DIR)


    def test_add_aliases_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_aliases_argument(parser, TOOL_NAME)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'alias_file' not in args     # no default

        args = vars(parser.parse_args(['-a', 'aliases.ini']))
        print(args)
        assert 'alias_file' in args

        args = vars(parser.parse_args(['--aliases', '/fake/aliases.ini']))
        print(args)
        assert 'alias_file' in args


    def test_add_catalog_hdu_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_catalog_hdu_argument(parser, TOOL_NAME)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'catalog_hdu' in args          # it has a default
        assert args.get('catalog_hdu') == 1   # zero is the default

        args = vars(parser.parse_args(['-chdu', '2']))
        print(args)
        assert 'catalog_hdu' in args
        assert args.get('catalog_hdu') == 2


    def test_add_catalog_table_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_catalog_table_argument(parser, TOOL_NAME)

        with pytest.raises(SystemExit) as se:
            args = vars(parser.parse_args([])) # catalog table name is required
        assert se.type == SystemExit

        args = vars(parser.parse_args(['-ct', 'cat_table_name']))
        print(args)
        assert 'catalog_table' in args

        args = vars(parser.parse_args(['--catalog-table', 'catalog_table_name']))
        print(args)
        assert 'catalog_table' in args


    def test_add_collection_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_collection_argument(parser, TOOL_NAME)

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
        utils.add_database_arguments(parser, TOOL_NAME)

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


    def test_add_fields_info_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_fields_info_argument(parser, TOOL_NAME)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'fields_file' not in args    # no default

        args = vars(parser.parse_args(['-fi', 'fields_file.ini']))
        print(args)
        assert 'fields_file' in args

        args = vars(parser.parse_args(['--fields-info', '/fake/fields_file.ini']))
        print(args)
        assert 'fields_file' in args


    def test_add_fits_file_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_fits_file_argument(parser, TOOL_NAME)

        with pytest.raises(SystemExit) as se:
            args = vars(parser.parse_args([])) # fits-file is required
        assert se.type == SystemExit

        args = vars(parser.parse_args(['-ff', 'astro.fits']))
        print(args)
        assert 'fits_file' in args
        assert 'which_hdu' not in args


    def test_add_hdu_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_hdu_argument(parser, TOOL_NAME)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'which_hdu' in args          # it has a default
        assert args.get('which_hdu') == 0   # zero is the default

        args = vars(parser.parse_args(['--hdu', '1']))
        print(args)
        assert 'which_hdu' in args
        assert args.get('which_hdu') == 1


    def test_add_ignore_list_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_ignore_list_argument(parser, TOOL_NAME)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'ignore_list' not in args

        args = vars(parser.parse_args(['--ig', 'COMMENT']))
        print(args)
        assert 'ignore_list' in args
        iglist = args.get('ignore_list')
        assert iglist is not None
        assert len(iglist) == 1

        args = vars(parser.parse_args(['--ig', 'HISTORY', '--ig', 'COMMENT']))
        print(args)
        assert 'ignore_list' in args
        iglist = args.get('ignore_list')
        assert iglist is not None
        assert len(iglist) == 2


    def test_add_input_file_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_input_file_argument(parser, TOOL_NAME)

        args = vars(parser.parse_args([]))
        print(args)
        assert 'input_file' not in args     # no default

        args = vars(parser.parse_args(['-if', 'metadata.json']))
        print(args)
        assert 'input_file' in args

        args = vars(parser.parse_args(['--input-file', '/fake/metadata.json']))
        print(args)
        assert 'input_file' in args


    def test_add_input_dir_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_input_dir_argument(parser, TOOL_NAME)

        with pytest.raises(SystemExit) as se:
            args = vars(parser.parse_args([])) # input-dir is required
        assert se.type == SystemExit

        args = vars(parser.parse_args(['-idir', self.resources_tstdir]))
        print(args)
        assert 'input_dir' in args

        args = vars(parser.parse_args(['--input-dir', '/tmp']))
        print(args)
        assert 'input_dir' in args


    def test_add_output_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_output_arguments(parser, TOOL_NAME)

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


    def test_add_report_format_argument(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        utils.add_report_format_argument(parser, TOOL_NAME)

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
        utils.add_shared_arguments(parser, TOOL_NAME)

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
        assert se.value.code == utils.ALIAS_FILE_EXIT_CODE


    def test_check_catalog_table(self):
        with pytest.raises(SystemExit) as se:
            utils.check_catalog_table('', TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == utils.CATALOG_TABLE_EXIT_CODE


    def test_check_dbconfig_file(self):
        with pytest.raises(SystemExit) as se:
            utils.check_dbconfig_file(self.nosuch_tstfyl, TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == utils.DBCONFIG_FILE_EXIT_CODE


    def test_check_fields_file(self):
        with pytest.raises(SystemExit) as se:
            utils.check_fields_file(self.nosuch_tstfyl, TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == utils.FIELDS_FILE_EXIT_CODE


    def test_check_fits_file_bad(self):
        with pytest.raises(SystemExit) as se:
            utils.check_fits_file(self.nosuch_tstfyl, TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == utils.FITS_FILE_EXIT_CODE


    def test_check_fits_file(self):
        try:
            utils.check_fits_file(self.m13_tstfyl, TOOL_NAME)
        except SystemExit as se:
            pytest.fail("test_cli_utils.test_check_fits_file: unexpected SystemExit: {}".format(repr(se)))


    def test_check_input_dir_bad(self):
        with pytest.raises(SystemExit) as se:
            utils.check_input_dir(self.nosuch_tstfyl, TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == utils.INPUT_DIR_EXIT_CODE


    def test_check_input_dir(self):
        try:
            utils.check_input_dir(self.resources_tstdir, TOOL_NAME)
        except SystemExit as se:
            pytest.fail("test_cli_utils.test_check_input_dir: unexpected SystemExit: {}".format(repr(se)))


    def test_check_input_file(self):
        with pytest.raises(SystemExit) as se:
            utils.check_input_file(self.nosuch_tstfyl, TOOL_NAME)
        assert se.type == SystemExit
        assert se.value.code == utils.INPUT_FILE_EXIT_CODE
