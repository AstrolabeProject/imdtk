# Tests for the iRods interface module.
#   Written by: Tom Hicks. 11/5/20.
#   Last Modified: Initial creation.
#
import os
import pytest

import astropy

import imdtk.exceptions as errors
import imdtk.core.fits_irods_helper as firh

from config.settings import DEFAULT_IRODS_AUTH_FILEPATH, DEFAULT_IRODS_ENV_FILEPATH
from imdtk.core import FitsHeaderInfo
from tests import TEST_DIR


class TestIRods(object):

    m13_tstfyl = "{}/resources/m13.fits".format(TEST_DIR)
    irff_hh = '/iplant/home/hickst/vos/images/HorseHead.fits'
    hdr0_size_hh = 14400                    # size of primary header
    hdr1_size_hh = 2880                     # size of first extension
    irff_m13 = '/iplant/home/hickst/vos/images/m13.fits'
    hdr0_size_m13 = 2880                    # size of primary header


    def test_create_helper_noconn (self):
        args = {}
        ihelper = firh.FitsIRodsHelper(args, connect=False)
        print(ihelper)
        assert ihelper is not None


    def test_create_helper_noargs (self):
        args = {}
        ihelper = firh.FitsIRodsHelper(args)
        print(ihelper)
        assert ihelper is not None


    def test_get_authentication_file (self):
        args = {}
        ihelper = firh.FitsIRodsHelper(args, connect=False)
        print(ihelper)
        assert ihelper is not None

        auth_file = ihelper.get_authentication_file(args)
        print(auth_file)
        assert auth_file is not None
        assert auth_file == DEFAULT_IRODS_AUTH_FILEPATH


    def test_get_environment_file (self):
        args = {}
        ihelper = firh.FitsIRodsHelper(args, connect=False)
        print(ihelper)
        assert ihelper is not None

        env_file = ihelper.get_environment_file(args)
        print(env_file)
        assert env_file is not None
        assert env_file == DEFAULT_IRODS_ENV_FILEPATH



    def test_calc_data_length (self):
        args = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestFitsIrodsHelper' }
        ihelper = firh.FitsIRodsHelper(args)
        print(ihelper)
        assert ihelper is not None

        irff = ihelper.getf(self.irff_m13, absolute=True)
        assert irff is not None

        with irff.open('r+') as irff_fd:
            hdr_info = ihelper.read_header(irff_fd, irff.size)
            print(hdr_info)
            assert hdr_info is not None
            dlen = ihelper.calc_data_length(hdr_info)
            print("DLEN={}".format(dlen))
        assert dlen != 0
        assert dlen == 181440




    # def test_read_header_at_offset0 (self):
    #     args = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestFitsIrodsHelper' }
    #     ihelper = firh.FitsIRodsHelper(args)
    #     print(ihelper)
    #     assert ihelper is not None

    #     irff = ihelper.getf(self.irff_hh, absolute=True)
    #     assert irff is not None

    #     with irff.open('r+') as irff_fd:
    #         hdr_info = ihelper.read_header_at_offset(irff_fd, 0, irff.size)
    #     print(hdr_info)
    #     assert hdr_info is not None
    #     assert hdr_info.offset == 0
    #     assert hdr_info.length == firh.FITS_BLOCK_SIZE * 5
    #     assert hdr_info.hdr is not None
    #     assert isinstance(hdr_info.hdr, astropy.io.fits.header.Header)


    # def test_read_header_at_offset1 (self):
    #     args = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestFitsIrodsHelper' }
    #     ihelper = firh.FitsIRodsHelper(args)
    #     print(ihelper)
    #     assert ihelper is not None

    #     irff = ihelper.getf(self.irff_hh, absolute=True)
    #     assert irff is not None

    #     with irff.open('r+') as irff_fd:
    #         hdr_info = ihelper.read_header_at_offset(irff_fd, 1607040, irff.size)
    #     print(hdr_info)
    #     assert hdr_info is not None
    #     assert hdr_info.offset == 1607040
    #     assert hdr_info.length == firh.FITS_BLOCK_SIZE
    #     assert hdr_info.hdr is not None
    #     assert isinstance(hdr_info.hdr, astropy.io.fits.header.Header)


    def test_read_header0 (self):
        args = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestFitsIrodsHelper' }
        ihelper = firh.FitsIRodsHelper(args)
        print(ihelper)
        assert ihelper is not None

        irff = ihelper.getf(self.irff_hh, absolute=True)
        assert irff is not None

        with irff.open('r+') as irff_fd:
            hdr_info = ihelper.read_header(irff_fd, irff.size)
        print(hdr_info)
        assert hdr_info is not None
        assert hdr_info.offset == 0
        assert hdr_info.length == self.hdr0_size_hh
        assert hdr_info.hdr is not None
        assert isinstance(hdr_info.hdr, astropy.io.fits.header.Header)


    def test_read_header1 (self):
        args = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestFitsIrodsHelper' }
        ihelper = firh.FitsIRodsHelper(args)
        print(ihelper)
        assert ihelper is not None

        irff = ihelper.getf(self.irff_hh, absolute=True)
        assert irff is not None

        hdr1_pos = 1607040                  # absolute offset of extension header

        with irff.open('r+') as irff_fd:
            irff_fd.seek(hdr1_pos, 0)       # seek absolute to the extension header
            hdr_info = ihelper.read_header(irff_fd, irff.size)
        print(hdr_info)
        assert hdr_info is not None
        assert hdr_info.offset == hdr1_pos
        assert hdr_info.length == self.hdr1_size_hh
        assert hdr_info.hdr is not None
        assert isinstance(hdr_info.hdr, astropy.io.fits.header.Header)
