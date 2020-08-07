# Tests for the alias utilities module.
#   Written by: Tom Hicks. 8/6/2020.
#   Last Modified: Initial creation: tests for keep_aliased_fields only.
#
import imdtk.core.alias_utils as utils


class TestAliasUtils(object):

    testdict = {'a': True, 'b': False, 'c': 0, 'd': 1, 'e': {}, 'f': {1: 1},
                'g': [], 'h': [1], 'i': None, 'j': 'Jstr', 'k': 99.9}
    testvec = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']


    def test_keep_aliased_fields_empty_dict (self):
        empty = dict()
        vec = utils.keep_aliased_fields(empty, self.testvec)
        assert vec == []


    def test_keep_aliased_fields_dict (self):
        vec = utils.keep_aliased_fields(self.testdict, self.testvec)
        print(vec)
        assert vec == [True, False, 0, 1, {}, {1: 1}, [], [1], 'Jstr', 99.9]
