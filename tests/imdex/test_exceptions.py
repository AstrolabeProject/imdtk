import imdtk.core.exceptions as xcpt

import os
import pytest


class TestExceptions(object):

    BAD_REQUEST = 'Bad Request'
    BAD_FILE = 'File XXX.bad Not Found'
    FAULT = 'Something went wrong'

    def test_request_exception(self):
        reqex = xcpt.RequestException(self.BAD_REQUEST)
        print(reqex)
        print(type(reqex))
        assert reqex.status_code == 400
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.BAD_REQUEST
        rtup = reqex.to_tuple()
        assert rtup[0] == self.BAD_REQUEST
        assert rtup[1] == 400


    def test_request_exception_withcode(self):
        reqex= xcpt.RequestException(self.BAD_REQUEST, 555)
        assert reqex.status_code == 555
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.BAD_REQUEST
        rtup = reqex.to_tuple()
        assert rtup[0] == self.BAD_REQUEST
        assert rtup[1] == 555


    def test_file_not_found(self):
        reqex = xcpt.FileNotFound(self.BAD_FILE)
        print(reqex)
        print(type(reqex))
        assert reqex.status_code == 404
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.BAD_FILE
        rtup = reqex.to_tuple()
        assert rtup[0] == self.BAD_FILE
        assert rtup[1] == 404


    def test_file_not_found_withcode(self):
        reqex= xcpt.FileNotFound(self.BAD_FILE, 99)
        assert reqex.status_code == 99
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.BAD_FILE
        rtup = reqex.to_tuple()
        assert rtup[0] == self.BAD_FILE
        assert rtup[1] == 99


    def test_processing_exception(self):
        reqex = xcpt.ProcessingException(self.FAULT)
        print(reqex)
        print(type(reqex))
        assert reqex.status_code == 500
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.FAULT
        rtup = reqex.to_tuple()
        assert rtup[0] == self.FAULT
        assert rtup[1] == 500


    def test_processing_exception_withcode(self):
        reqex= xcpt.ProcessingException(self.FAULT, 7)
        assert reqex.status_code == 7
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.FAULT
        rtup = reqex.to_tuple()
        assert rtup[0] == self.FAULT
        assert rtup[1] == 7
