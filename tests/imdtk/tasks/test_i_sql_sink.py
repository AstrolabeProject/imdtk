# Tests for the ISQLSink.
#   Written by: Tom Hicks. 8/8/2020.
#   Last Modified: Initial creation: test load_sql_db_config only.
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
