# Tests for the misc utilities module.
#   Written by: Tom Hicks. 5/22/2020.
#   Last Modified: Add another test for get_in.
#
import os
import pytest

import imdtk.core.misc_utils as mutils


class TestMiscUtils(object):

    def test_get_in (self):
        nester = { 'a': 'a',
                   'L1': { 'a': 'a',
                           'L2': { 'a': 'a',
                                   'badval': [],
                                   'L3': { 'a': 'a',
                                           'L4': {} } } } }

        assert mutils.get_in(nester, ['a']) == 'a'
        assert mutils.get_in(nester, ['L1', 'a']) == 'a'
        assert mutils.get_in(nester, ['L1', 'L2', 'a']) == 'a'
        assert mutils.get_in(nester, ['L1', 'L2', 'L3', 'a']) == 'a'

        assert mutils.get_in(nester, []) is None
        assert mutils.get_in(nester, ['b']) is None
        assert mutils.get_in(nester, ['L1', 'b']) is None
        assert mutils.get_in(nester, ['L1', 'L2', 'b']) is None
        assert mutils.get_in(nester, ['L1', 'L2', 'L3', 'b']) is None
        assert mutils.get_in(nester, ['L1', 'L2', 'L3', 'L4', 'b']) is None
        assert mutils.get_in(nester, ['L1', 'L2', 'L3', 'L4', 'a']) is None

        assert mutils.get_in(nester, ['L1']) is not None
        assert isinstance(mutils.get_in(nester, ['L1']), dict)
        assert mutils.get_in(nester, ['L1', 'L2']) is not None
        assert isinstance(mutils.get_in(nester, ['L1', 'L2']), dict)
        assert mutils.get_in(nester, ['L1', 'L2', 'L3']) is not None
        assert isinstance(mutils.get_in(nester, ['L1', 'L2', 'L3']), dict)
        assert mutils.get_in(nester, ['L1', 'L2', 'L3', 'L4']) is not None
        assert isinstance(mutils.get_in(nester, ['L1', 'L2', 'L3', 'L4']), dict)
        assert mutils.get_in(nester, ['L1', 'L2', 'badval', 'nosuchkey']) is None



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
