# Tests methods of the headers module.
#   Written by: Tom Hicks. 5/21/2020.
#   Last Modified: Initial creation: begin to move methods from other test files.
#
import os
import pytest

import imdtk.tools.headers as headers


class TestHeaders(object):

    def test_filter_header_fields_default (self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        headers.filter_header_fields(hdrs) # modifies by side-effect
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
        headers.filter_header_fields(hdrs, ignore=['HISTORY', 'history'])
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
        headers.filter_header_fields(hdrs, ignore=keys)
        print(hdrs)
        assert len(hdrs) == 0
        assert 'HISTORY' not in hdrs
        assert 'history' not in hdrs
        assert 'COMMENT' not in hdrs
        assert 'comment' not in hdrs
