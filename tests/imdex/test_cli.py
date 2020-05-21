# Tests of main CLI module.
#   Written by: Tom Hicks. 2/19/2020.
#   Last Modified: Update tests for no output directory argument.
#
from imdtk import cli

import os
import pytest
from pathlib import Path


class TestCLI(object):

    nosuch_file = 'NOSUCHFILE'
    nosuch_path = 'tests/resources/NOSUCHFILE'
    m13_file = 'tests/resources/m13.fits'

    def test_check_filepath (self):
        newpath = '/tmp/HiGhLy_UnLiKeLy2'
        newbie = Path(newpath)
        sympath = '/tmp/linkToHiGhLy_UnLiKeLy2'
        sympie = Path(sympath)
        sympie.symlink_to(newpath)
        newbie.touch(mode=0o444)

        assert cli.check_filepath('.fits') == False
        assert cli.check_filepath('.fits', '') == False
        assert cli.check_filepath('.fits', 'test file') == False
        assert cli.check_filepath('') == False
        assert cli.check_filepath('', '') == False
        assert cli.check_filepath('', 'empty filepath') == False
        assert cli.check_filepath('BADfile') == False
        assert cli.check_filepath('BADfile', '') == False
        assert cli.check_filepath('BADfile', 'test file') == False
        assert cli.check_filepath('/tmp/BADFILE') == False
        assert cli.check_filepath('/tmp/BADFILE', '') == False
        assert cli.check_filepath('/tmp/BADFILE', 'test file') == False

        assert cli.check_filepath(None) == True
        assert cli.check_filepath(None, '') == True
        assert cli.check_filepath(None, 'no filepath given') == True
        assert cli.check_filepath(newpath) == True
        assert cli.check_filepath(newpath, '') == True
        assert cli.check_filepath(newpath, 'good filepath') == True
        assert cli.check_filepath(sympie) == True
        assert cli.check_filepath(sympie, '') == True
        assert cli.check_filepath(sympie, 'good filepath') == True


    def test_main_no_argv (self):
        with pytest.raises(SystemExit) as se:
            cli.main()



    def test_main_alias_file_arg (self):
        with pytest.raises(SystemExit) as se:
            cli.main(['--aliases', self.nosuch_file, '/images'])
        assert se.type == SystemExit
        assert se.value.code == 10


    def test_main_db_file_arg (self):
        with pytest.raises(SystemExit) as se:
            cli.main(['--dbconfig', self.nosuch_file, '/images'])
        assert se.type == SystemExit
        assert se.value.code == 11


    def test_main_fields_file_arg (self):
        with pytest.raises(SystemExit) as se:
            cli.main(['--field-info', self.nosuch_file, '/images'])
        assert se.type == SystemExit
        assert se.value.code == 12



    def test_main_image_paths_none (self):
        with pytest.raises(SystemExit) as se:
            cli.main(['-v'])
        assert se.type == SystemExit
        assert se.value.code == 2           # argparse exit == 2


    def test_main_image_paths_1bad (self):
        with pytest.raises(SystemExit) as se:
            cli.main([self.nosuch_file])
        assert se.type == SystemExit
        assert se.value.code == 21


    def test_main_image_paths_2bad (self):
        with pytest.raises(SystemExit) as se:
            cli.main([self.nosuch_file, self.nosuch_path])
        assert se.type == SystemExit
        assert se.value.code == 21


    def test_main_bad_processor (self):
        with pytest.raises(SystemExit) as se:
            cli.main(['--processor', 'hunter', '/images'])
        assert se.type == SystemExit
        assert se.value.code == 22


    def test_main_default_processor (self):
        try:
            cli.main(['-of', 'sql', '-v', '/images'])
        except SystemExit as se:
            pytest.fail("test_main_default_processor: unexpected SystemExit: {}".format(repr(se)))


    def test_main_jwst_processor (self):
        try:
            cli.main(['-of', 'sql', '-v', '--processor', 'jwst', '/images'])
        except SystemExit as se:
            pytest.fail("test_main_jwst_processor: unexpected SystemExit: {}".format(repr(se)))


    # exercise directory processing path in main method
    def test_main_dir_path (self):
        try:
            cli.main(['-of', 'sql', '-v', '/images'])
        except SystemExit as se:
            pytest.fail("test_main_dir_path: unexpected SystemExit: {}".format(repr(se)))


    # exercise file processing path in main method
    def test_main_file_path (self):
        try:
            cli.main(['-of', 'sql', '-v', '-d', self.m13_file])
        except SystemExit as se:
            pytest.fail("test_main_file_path: unexpected SystemExit: {}".format(repr(se)))
