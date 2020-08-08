# Tests for the FieldsInfoTask.
#   Written by: Tom Hicks. 8/8/2020.
#   Last Modified: Initial creation: test non-interface methods only.
#
import pytest
from pytest import approx

import imdtk.exceptions as errors
import imdtk.tasks.fields_info as fit
from tests import TEST_DIR


class TestFieldsInfoTask(object):

    empty_fields_tstfyl = "{}/resources/test-fields-empty.toml".format(TEST_DIR)
    fields_tstfyl = "{}/resources/test-fields.toml".format(TEST_DIR)
    nosuch_tstfyl = '/tests/resources/NOSUCHFILE'

    args = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestFieldsInfoTask' }


    def test_load_fields_info_bad(self):
        task = fit.FieldsInfoTask(self.args)
        with pytest.raises(errors.ProcessingError, match='not found or not readable'):
            task.load_fields_info(self.nosuch_tstfyl)


    def test_load_fields_info_empty(self):
        task = fit.FieldsInfoTask(self.args)
        task.load_fields_info(self.empty_fields_tstfyl)


    def test_load_fields_info(self):
        task = fit.FieldsInfoTask(self.args)

        finfo = task.load_fields_info(self.fields_tstfyl)
        print(finfo)
        assert finfo is not None
        assert len(finfo) >= 8               # specific to this test file

        assert 'dataproduct_type' in finfo
        assert 'calib_level' in finfo
        assert 'filter' in finfo
        assert 'is_public' in finfo
        pub = finfo.get('is_public')
        assert pub is not None
        assert len(pub) > 0
        assert 'required' in pub
        assert pub.get('default') == 0
        assert finfo.get('filter').get('required') is False



    def test_extract_defaults(self):
        task = fit.FieldsInfoTask(self.args)

        finfo = task.load_fields_info(self.fields_tstfyl)
        print(finfo)
        assert finfo is not None

        defaults = task.extract_defaults(finfo)
        assert defaults is not None
        assert len(defaults) > 0
        assert 'dataproduct_type' in defaults
        assert defaults.get('dataproduct_type') == 'image'
        assert 'equinox' in defaults
        assert defaults.get('equinox') == 2000.0
        assert 'is_public' in defaults
        assert defaults.get('is_public') == 0

        assert 'filter' not in defaults
        assert 'target_name' not in defaults
