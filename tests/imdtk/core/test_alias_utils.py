# Tests for the alias utilities module.
#   Written by: Tom Hicks. 8/6/2020.
#   Last Modified: Add tests for copy_aliased_headers.
#
import imdtk.core.alias_utils as utils


class TestAliasUtils(object):

    alfadic = {'a': True, 'b': False, 'c': 0, 'd': 1, 'e': {}, 'f': {1: 1},
               'g': [], 'h': [1], 'i': None, 'j': 'Jstr', 'k': 99.9}
    alfavec = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']

    testhdrs = {
        "SIMPLE": True,
        "BITPIX": -64,
        "NAXIS": 2,
        "NAXIS1": 9791,
        "NAXIS2": 4305,
        "DATE": "2019-12-14T21:10:36.490",
        "TIMESYS": "UTC",
        "WCSAXES": 2,
        "RA": 53.157662568,
        "DEC": -27.8075199236
    }

    aliases = {
        "NAXIS": "im_naxes",
        "NAXIS1": "s_xel1",
        "NAXIS2": "s_xel2",
        "RA": "s_ra",
        "DEC": "s_dec"
    }


    def test_keep_aliased_fields_empty_dict (self):
        empty = dict()
        vec = utils.keep_aliased_fields(empty, self.alfavec)
        assert vec == []


    def test_keep_aliased_fields_dict (self):
        vec = utils.keep_aliased_fields(self.alfadic, self.alfavec)
        print(vec)
        assert vec == [True, False, 0, 1, {}, {1: 1}, [], [1], 'Jstr', 99.9]



    def test_copy_aliased_headers_empty (self):
        empty = dict()
        newdic = utils.copy_aliased_headers(empty, empty)
        print(newdic)
        assert newdic == {}
        assert len(newdic) == 0


    def test_copy_aliased_headers_nohdrs (self):
        empty = dict()
        newdic = utils.copy_aliased_headers(self.aliases, empty)
        print(newdic)
        assert newdic == {}
        assert len(newdic) == 0


    def test_copy_aliased_headers_noalias (self):
        empty = dict()
        newdic = utils.copy_aliased_headers(empty, self.testhdrs)
        print(newdic)
        assert newdic == {}
        assert len(newdic) == 0


    def test_copy_aliased_headers (self):
        newdic = utils.copy_aliased_headers(self.aliases, self.testhdrs)
        print(newdic)
        assert newdic is not None
        assert len(newdic) == 5
        assert "im_naxes" in newdic
        assert newdic.get("im_naxes") == 2
        assert "s_xel1" in newdic
        assert newdic.get("s_xel1") == 9791
        assert "s_ra" in newdic
        assert newdic.get("s_ra") == 53.157662568

        assert "NAXIS" not in newdic
        assert "NAXIS2" not in newdic
        assert "RA" not in newdic
        assert "DEC" not in newdic
