# Tests for the misc utilities module.
#   Written by: Tom Hicks. 5/22/2020.
#   Last Modified: Initial creation.
#
import os
import pytest

import imdtk.core.misc_utils as mutils


class TestMiscUtils(object):

    def test_remove_entries_default (self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        mutils.remove_entries(hdrs) # modifies by side-effect
        print(hdrs)
        assert len(hdrs) == old_len
        assert 'HISTORY' in hdrs
        assert 'COMMENT' in hdrs
        assert 'history' in hdrs
        assert 'comment' in hdrs


    def test_remove_entries_ignore_nonexist (self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        mutils.remove_entries(hdrs, ignore=['AAA', 'pikey']) # modifies by side-effect
        print(hdrs)
        assert len(hdrs) == old_len
        assert 'AA' in hdrs
        assert 'pi' in hdrs
        assert 'AAA' not in hdrs
        assert 'pikey' not in hdrs


    def test_remove_entries_ignore_empty (self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        mutils.remove_entries(hdrs, ignore=[]) # modifies by side-effect
        print(hdrs)
        assert len(hdrs) == old_len
        assert 'AA' in hdrs
        assert 'pi' in hdrs
        assert 'HISTORY' in hdrs
        assert 'COMMENT' in hdrs
        assert 'history' in hdrs
        assert 'comment' in hdrs


    def test_remove_entries_nohist (self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        mutils.remove_entries(hdrs, ignore=['HISTORY', 'history'])
        print(hdrs)
        assert len(hdrs) == (old_len - 2)
        assert 'HISTORY' not in hdrs
        assert 'history' not in hdrs
        assert 'COMMENT' in hdrs
        assert 'comment' in hdrs


    def test_remove_entries_all (self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        keys = list(hdrs.keys()).copy()     # prevent change-during-iteration error
        mutils.remove_entries(hdrs, ignore=keys)
        print(hdrs)
        assert len(hdrs) == 0
        assert 'HISTORY' not in hdrs
        assert 'history' not in hdrs
        assert 'COMMENT' not in hdrs
        assert 'comment' not in hdrs
