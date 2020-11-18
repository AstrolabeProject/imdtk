# Tests for the iRods interface module DEVELOPMENT.
#   Written by: Tom Hicks. 11/18/20.
#   Last Modified: Initial creation for DEVELOPMENT.
#
import os, sys
import pytest

import astropy

import imdtk.exceptions as errors
import imdtk.core.fits_irods_helper as firh

import imdtk.core.fits_utils as fits_utils
from config.settings import DEFAULT_IRODS_AUTH_FILEPATH, DEFAULT_IRODS_ENV_FILEPATH
from imdtk.core import FitsHeaderInfo
from tests import TEST_DIR


class TestIRods(object):

    defargs = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestFitsIrodsHelper' }

    irff_m13 = '/iplant/home/hickst/vos/images/m13.fits'
    hdr0_size_m13 = 2880                    # size of primary header
    hdr0_datasize_m13 = 181440              # size of primary data table

    irff_hh = '/iplant/home/hickst/vos/images/HorseHead.fits'
    hdr0_size_hh = 14400                    # size of primary header
    hdr0_datasize_hh = 1592640              # size of primary data table
    hdr1_size_hh = 2880                     # size of first extension
    hdr1_datasize_hh = 40320                # size of first extension data table

    irff_BAD =      '/iplant/home/hickst/vos/images/BAD.fits'
    irff_smallcat = '/iplant/home/hickst/vos/catalogs/small_table.fits'


    def test_get_hdu_at_smallcat (self):
        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None

        irff = ihelper.getf(self.irff_smallcat, absolute=True)
        assert irff is not None

        with irff.open('r+') as irff_fd:
            hdu = ihelper.get_hdu_at(irff_fd, irff.size, which_hdu=1)
            assert hdu is not None
            col_md = hdu.columns.info(output=False)
            print("COL_MD={}".format(col_md), file=sys.stderr)
            assert col_md is not None
            assert len(col_md) == 15
            for fld in ['name', 'format', 'unit', 'bscale', 'bzero']:
                assert fld in col_md
            assert len(col_md['name']) == 18


    def test_devel (self):
        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None

        irff = ihelper.getf(self.irff_smallcat, absolute=True)
        assert irff is not None

        with irff.open('r+') as irff_fd:
            hdr_info = ihelper.get_header_info_at(irff_fd, irff.size, which_hdu=1)
            # print("HDR_INFO={}".format(hdr_info), file=sys.stderr)
            datalen = ihelper.calc_data_length(hdr_info.hdr)
            # print("DATALEN={}".format(datalen), file=sys.stderr)
            hdu_len = hdr_info.length + datalen
            # print("HDU_LEN={}".format(hdu_len), file=sys.stderr)

            irff_fd.seek(hdr_info.offset, 0)  # seek to start of HDU
            # print("SEEKPOS={}".format(irff_fd.tell()), file=sys.stderr)
            # hdu_data = irff_fd.read(hdu_len)  # read HDU bytes
            hdu_data = ihelper.read_chunk(irff_fd, irff.size, hdu_len)  # read HDU bytes
            # print("len(hdu_data)={}".format(len(hdu_data)), file=sys.stderr)
            hdulist = astropy.io.fits.hdu.hdulist.HDUList.fromstring(hdu_data)
            # print("HDULIST={}".format(hdulist), file=sys.stderr)

            col_md = hdulist[0].columns.info(output=False)
            print("COL_MD={}".format(col_md), file=sys.stderr)

        # assert False                        # in order to see outputs
