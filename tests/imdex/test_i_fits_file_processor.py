# Tests of IFitsFileProcessor abstract base class.
#   Written by: Tom Hicks. 4/7/2020.
#   Last Modified: Update tests for no output directory argument.
#
import os
import pytest

from imdtk.core.jwst_processor import JwstProcessor
from imdtk.core.field_info import FieldInfo
from imdtk.core.fields_info import FieldsInfo


class TestIFitsFileProcessor(object):

    debug_args = {
        'alias_file': None,
        'collection': None,
        'debug': True,
        'db_config_file': None,
        'fields_file': None,
        'output_format': 'sql',
        'processor_type': 'jwst',
        'verbose': True,
        'image_paths': [ '/images/m13.fits' ]
    }
    debproc = JwstProcessor(debug_args)


    def test_filter_header_fields_default (self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        self.debproc.filter_header_fields(hdrs) # modifies by side-effect
        print(hdrs)
        assert len(hdrs) == (old_len - 2)
        assert 'HISTORY' not in hdrs
        assert 'COMMENT' not in hdrs
        assert 'history' in hdrs
        assert 'comment' in hdrs


    def test_filter_header_fields_nohist (self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        self.debproc.filter_header_fields(hdrs, ignore=['HISTORY', 'history'])
        print(hdrs)
        assert len(hdrs) == (old_len - 2)
        assert 'HISTORY' not in hdrs
        assert 'history' not in hdrs
        assert 'COMMENT' in hdrs
        assert 'comment' in hdrs


    def test_filter_header_fields_all (self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        keys = list(hdrs.keys()).copy()     # prevent change-during-iteration error
        self.debproc.filter_header_fields(hdrs, ignore=keys)
        print(hdrs)
        assert len(hdrs) == 0
        assert 'HISTORY' not in hdrs
        assert 'history' not in hdrs
        assert 'COMMENT' not in hdrs
        assert 'comment' not in hdrs
