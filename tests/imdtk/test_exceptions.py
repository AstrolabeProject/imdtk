# Tests for the exceptions module.
#   Written by: Tom Hicks. 7/20/2020.
#   Last Modified: Initial creation.
#
import pytest

import imdtk.exceptions as xcpt


class TestExceptions(object):

    ECODE = 888
    EMSG = 'Something went wrong'
    BADFYL = 'Wrong type: file XXX.bad'

    def test_pe (self):
        pe = xcpt.ProcessingError(self.EMSG)
        print(pe)
        print(type(pe))
        assert pe.error_code == xcpt.ProcessingError.ERROR_CODE
        pedict = pe.to_dict()
        assert 'message' in pedict
        assert 'error_code' in pedict
        assert pedict.get('message') == self.EMSG
        assert pedict.get('error_code') == xcpt.ProcessingError.ERROR_CODE
        petup = pe.to_tuple()
        assert petup[0] == self.EMSG
        assert petup[1] == xcpt.ProcessingError.ERROR_CODE


    def test_pe_code (self):
        pe = xcpt.ProcessingError(self.EMSG, self.ECODE)
        print(pe)
        print(type(pe))
        assert pe.error_code == self.ECODE
        pedict = pe.to_dict()
        assert 'message' in pedict
        assert 'error_code' in pedict
        assert pedict.get('message') == self.EMSG
        assert pedict.get('error_code') == self.ECODE
        petup = pe.to_tuple()
        assert petup[0] == self.EMSG
        assert petup[1] == self.ECODE


    def test_ute (self):
        ute = xcpt.UnsupportedTypeError(self.EMSG)
        print(ute)
        print(type(ute))
        assert ute.error_code == xcpt.UnsupportedTypeError.ERROR_CODE
        utedict = ute.to_dict()
        assert 'message' in utedict
        assert 'error_code' in utedict
        assert utedict.get('message') == self.EMSG
        assert utedict.get('error_code') == xcpt.UnsupportedTypeError.ERROR_CODE
        utetup = ute.to_tuple()
        assert utetup[0] == self.EMSG
        assert utetup[1] == xcpt.UnsupportedTypeError.ERROR_CODE


    def test_ute_code (self):
        ute = xcpt.UnsupportedTypeError(self.EMSG, self.ECODE)
        print(ute)
        print(type(ute))
        assert ute.error_code == self.ECODE
        utedict = ute.to_dict()
        assert 'message' in utedict
        assert 'error_code' in utedict
        assert utedict.get('message') == self.EMSG
        assert utedict.get('error_code') == self.ECODE
        utetup = ute.to_tuple()
        assert utetup[0] == self.EMSG
        assert utetup[1] == self.ECODE
