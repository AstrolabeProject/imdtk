# Tests for the iRods interface module.
#   Written by: Tom Hicks. 11/5/20.
#   Last Modified: Add some tests for gen_fits_file_paths.
#
import os
import pytest

import astropy

import imdtk.exceptions as errors
import imdtk.core.fits_irods_helper as firh

from config.settings import DEFAULT_IRODS_AUTH_FILEPATH, DEFAULT_IRODS_ENV_FILEPATH
from imdtk.core import FitsHeaderInfo
from tests import TEST_DIR


class TestFitsIRodsHelper(object):

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


    def test_get_header_primary (self):
        """
        Also tests get_header_at, calculate_data_length, calc_data_length, read_header.
        """
        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None

        # read primary header
        irff = ihelper.getf(self.irff_m13, absolute=True)
        header = ihelper.get_header(irff)
        print(header)
        assert header is not None
        assert len(header) > 3              # 3 keywords are mandatory
        assert header.get('SIMPLE') is True
        assert header.get('NAXIS') == 2


    def test_get_header_extension (self):
        """
        Also tests get_header_at, calculate_data_length, calc_data_length, read_header.
        """
        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None

        # read primary header
        irff = ihelper.getf(self.irff_hh, absolute=True)
        header = ihelper.get_header(irff, which_hdu=1)
        print(header)
        assert header is not None
        assert len(header) > 5              # 5 keywords are mandatory
        assert header.get('SIMPLE') is None
        assert header.get('XTENSION') == 'TABLE'
        assert header.get('GCOUNT') == 1


    def test_get_header_fields_none (self):
        """ Also tests get_fields_from_header. """
        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None

        irff = ihelper.getf(self.irff_BAD, absolute=True)
        hflds = ihelper.get_header_fields(irff)
        assert hflds is None


    def test_get_header_fields (self):
        """ Also tests get_fields_from_header. """
        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None

        irff = ihelper.getf(self.irff_m13, absolute=True)
        hflds = ihelper.get_header_fields(irff)
        assert hflds is not None
        assert len(hflds) > 3               # 3 keywords are mandatory
        assert 'SIMPLE' in hflds
        assert 'BITPIX' in hflds
        assert 'NAXIS' in hflds
        assert 'EXTEND' in hflds
        assert hflds.get('CTYPE1') == 'RA---TAN'
        assert hflds.get('CTYPE2') == 'DEC--TAN'


    def test_get_irods_file_info (self):
        """ Also tests get_irods_file_metadata. """
        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None

        # read primary header
        irff = ihelper.getf(self.irff_hh, absolute=True)
        finfo = ihelper.get_irods_file_info(irff)
        assert finfo is not None
        assert len(finfo) == 3              # file path, name, size
        assert 'file_path' in finfo
        assert 'file_name' in finfo
        assert 'file_size' in finfo
        assert 'owner_zone' not in finfo
        assert 'name' not in finfo
        assert 'irods_metadata' not in finfo


    def test_is_catalog_header_m13 (self):
        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None
        irff = ihelper.getf(self.irff_m13, absolute=True)

        header = ihelper.get_header(irff)
        assert ihelper.is_catalog_header(header) is False

        header = ihelper.get_header(irff, which_hdu=1)
        assert ihelper.is_catalog_header(header) is False

        header = ihelper.get_header(irff, which_hdu=0)
        assert ihelper.is_catalog_header(header) is False


    def test_is_catalog_header_hh (self):
        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None
        irff = ihelper.getf(self.irff_hh, absolute=True)

        header = ihelper.get_header(irff)
        assert ihelper.is_catalog_header(header) is False

        header = ihelper.get_header(irff, which_hdu=1)
        assert ihelper.is_catalog_header(header) is True

        header = ihelper.get_header(irff, which_hdu=0)
        assert ihelper.is_catalog_header(header) is False

        header = ihelper.get_header(irff, which_hdu=3)
        assert ihelper.is_catalog_header(header) is False


    def test_is_catalog_header_smallcat (self):
        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None
        irff = ihelper.getf(self.irff_smallcat, absolute=True)

        header = ihelper.get_header(irff)
        assert ihelper.is_catalog_header(header) is False

        header = ihelper.get_header(irff, which_hdu=1)
        assert ihelper.is_catalog_header(header) is True

        header = ihelper.get_header(irff, which_hdu=0)
        assert ihelper.is_catalog_header(header) is False

        header = ihelper.get_header(irff, which_hdu=3)
        assert ihelper.is_catalog_header(header) is False



    def test_gen_fits_file_paths_none (self):
        empty_path = '/iplant/home/hickst/resources'

        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None

        irdir = ihelper.getc(empty_path, absolute=True)
        print("IRDIR={}".format(irdir))
        assert irdir is not None

        paths = [ fpath for fpath in ihelper.gen_fits_file_paths(irdir) ]
        assert paths is not None
        assert len(paths) < 1


    def test_gen_fits_file_paths (self):
        img_path = '/iplant/home/hickst/vos/images'

        ihelper = firh.FitsIRodsHelper(self.defargs)
        assert ihelper is not None

        irdir = ihelper.getc(img_path, absolute=True)
        print("IRDIR={}".format(irdir))
        assert irdir is not None

        paths = [ fpath for fpath in ihelper.gen_fits_file_paths(irdir) ]
        assert paths is not None
        assert len(paths) > 1
