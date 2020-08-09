# Tests for the ISQLSink.
#   Written by: Tom Hicks. 8/8/2020.
#   Last Modified: Add tests for file_info_to_comment_string.
#
import pytest

import imdtk.exceptions as errors
import imdtk.tasks.i_sql_sink as isql
from tests import TEST_DIR, TEST_DBCONFIG_FILEPATH


class TestISQLSink(object):

    dbconfig_tstfyl = TEST_DBCONFIG_FILEPATH
    empty_dbconfig_tstfyl = "{}/resources/test-dbconfig-empty.ini".format(TEST_DIR)
    noprops_dbconfig_tstfyl = "{}/resources/test-dbconfig-no-props.ini".format(TEST_DIR)
    nouri_dbconfig_tstfyl = "{}/resources/test-dbconfig-no-uri.ini".format(TEST_DIR)
    nosuch_tstfyl = '/tests/resources/NOSUCHFILE'

    args = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestISQLSink' }


    def test_file_info_to_comment_string_no_fi(self):
        task = isql.ISQLSink(self.args)
        fics = task.file_info_to_comment_string(None, None, None)
        assert fics is not None
        assert fics == task.SQL_COMMENT


    def test_file_info_to_comment_string_fname(self):
        task = isql.ISQLSink(self.args)
        fics = task.file_info_to_comment_string('file-name', None, None)
        assert fics is not None
        assert fics == task.SQL_COMMENT + ' file-name'


    def test_file_info_to_comment_string_fsize(self):
        task = isql.ISQLSink(self.args)
        fics = task.file_info_to_comment_string(None, 888, None)
        assert fics is not None
        assert fics == task.SQL_COMMENT + ' 888'


    def test_file_info_to_comment_string_fpath(self):
        task = isql.ISQLSink(self.args)
        fics = task.file_info_to_comment_string(None, None, '/tmp/file-name')
        assert fics is not None
        assert fics == task.SQL_COMMENT + ' /tmp/file-name'


    def test_file_info_to_comment_string(self):
        task = isql.ISQLSink(self.args)
        fics = task.file_info_to_comment_string('file-name', 999, '/path/file-name')
        assert fics is not None
        assert fics == task.SQL_COMMENT + ' file-name 999 /path/file-name'



    def test_load_sql_db_config_bad(self):
        task = isql.ISQLSink(self.args)
        with pytest.raises(errors.ProcessingError, match='not found or not readable'):
            task.load_sql_db_config(self.nosuch_tstfyl)


    def test_load_sql_db_config_no_props(self):
        task = isql.ISQLSink(self.args)
        with pytest.raises(errors.ProcessingError, match='no database parameters .* found'):
            task.load_sql_db_config(self.noprops_dbconfig_tstfyl)


    def test_load_sql_db_config_empty(self):
        task = isql.ISQLSink(self.args)
        with pytest.raises(errors.ProcessingError, match='no database parameters .* found'):
            task.load_sql_db_config(self.empty_dbconfig_tstfyl)


    def test_load_sql_db_config_no_uri(self):
        task = isql.ISQLSink(self.args)
        with pytest.raises(errors.ProcessingError, match='no database URI .* found'):
            task.load_sql_db_config(self.nouri_dbconfig_tstfyl)


    def test_load_sql_db_config(self):
        task = isql.ISQLSink(self.args)

        dbconf = task.load_sql_db_config(self.dbconfig_tstfyl)
        print(dbconf)
        assert dbconf is not None
        assert len(dbconf) >= 7               # specific to this test file
