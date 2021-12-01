# Tests for the iRods interface module.
#   Written by: Tom Hicks. 10/20/20.
#   Last Modified: Update to import TEST_IPLANT_DATA_ROOT.
#
import os
import pytest

import imdtk.exceptions as errors
from imdtk.core.irods_helper import IRodsHelper
from irods.exception import CollectionDoesNotExist
from tests import TEST_IPLANT_DATA_ROOT


class TestIRodsHelper(object):

    defargs = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestIrodsHelper' }

    irff_m13 = f"{TEST_IPLANT_DATA_ROOT}/images/m13.fits"
    hdr0_size_m13 = 2880                    # size of primary header
    hdr0_datasize_m13 = 181440              # size of primary data table

    irff_hh = f"{TEST_IPLANT_DATA_ROOT}/images/HorseHead.fits"
    hdr0_size_hh = 14400                    # size of primary header
    hdr0_datasize_hh = 1592640              # size of primary data table
    hdr1_size_hh = 2880                     # size of first extension
    hdr1_datasize_hh = 40320                # size of first extension data table

    irff_BAD =      f"{TEST_IPLANT_DATA_ROOT}/images/BAD.fits"
    irff_smallcat = f"{TEST_IPLANT_DATA_ROOT}/catalogs/small_table.fits"


    def test_ctor_defaults (self):
        """ Test defaults for iRods config directory, thus auth and env file locations. """
        args = {}
        ihelper = IRodsHelper({}, connect=False)
        print(ihelper)
        assert ihelper is not None
        assert ihelper.irods_config_dir is not None
        assert str(ihelper.irods_config_dir) == '/imdtk/.irods'
        assert ihelper.default_irods_auth_file is not None
        assert str(ihelper.default_irods_auth_file) == '/imdtk/.irods/.irodsA'
        assert ihelper.default_irods_env_file is not None
        assert str(ihelper.default_irods_env_file) == '/imdtk/.irods/irods_environment.json'


    def test_ctor_with_irdir (self):
        """ Test given path for iRods config directory, thus auth and env file locations. """
        args = {}
        ihelper = IRodsHelper({'irods_config_directory': '/tmp/.irods'}, connect=False)
        print(ihelper)
        assert ihelper is not None
        assert ihelper.irods_config_dir is not None
        assert str(ihelper.irods_config_dir) == '/tmp/.irods'
        assert ihelper.default_irods_auth_file is not None
        assert str(ihelper.default_irods_auth_file) == '/tmp/.irods/.irodsA'
        assert ihelper.default_irods_env_file is not None
        assert str(ihelper.default_irods_env_file) == '/tmp/.irods/irods_environment.json'


    def test_create_helper_noconn (self):
        args = {}
        ihelper = IRodsHelper(args, connect=False)
        print(ihelper)
        assert ihelper is not None


    def test_create_helper_noargs (self):
        args = {}
        ihelper = IRodsHelper(args)
        print(ihelper)
        assert ihelper is not None


    def test_get_authentication_file (self):
        args = {}
        ihelper = IRodsHelper(args, connect=False)
        print(ihelper)
        assert ihelper is not None

        auth_file = ihelper.get_authentication_file(args)
        print(auth_file)
        assert auth_file is not None
        assert auth_file == ihelper.default_irods_auth_file


    def test_get_environment_file (self):
        args = {}
        ihelper = IRodsHelper(args, connect=False)
        print(ihelper)
        assert ihelper is not None

        env_file = ihelper.get_environment_file(args)
        print(env_file)
        assert env_file is not None
        assert env_file == ihelper.default_irods_env_file


    def test_to_dirpath (self):
        args = {}
        ihelper = IRodsHelper(args, connect=False)

        ihelper.to_dirpath('/') == '/'
        ihelper.to_dirpath('.') == './'
        ihelper.to_dirpath('x') == 'x/'
        ihelper.to_dirpath('x/') == 'x/'
        ihelper.to_dirpath('abc') == 'abc/'
        ihelper.to_dirpath('abc/') == 'abc/'
        ihelper.to_dirpath('/a/b/c') == '/a/b/c/'
        ihelper.to_dirpath('/a/b/c/') == '/a/b/c/'


    def test_getc_badpath (self):
        bad_path = f"{TEST_IPLANT_DATA_ROOT}/images2"

        ihelper = IRodsHelper(self.defargs)
        assert ihelper is not None

        with pytest.raises(CollectionDoesNotExist):
            irdir = ihelper.getc(bad_path, absolute=True)


    def test_getc (self):
        img_path = f"{TEST_IPLANT_DATA_ROOT}/images"

        ihelper = IRodsHelper(self.defargs)
        assert ihelper is not None

        irdir = ihelper.getc(img_path, absolute=True)
        print("IRDIR={}".format(irdir))
        assert irdir is not None
        assert ihelper.is_collection(irdir)


    def test_put_metaf (self):
        ihelper = IRodsHelper(self.defargs)
        assert ihelper is not None

        irff = ihelper.getf(self.irff_m13, absolute=True)
        assert irff is not None

        for md in ihelper.get_metaf(self.irff_m13, absolute=True):
            print("{}={}".format(md.keyword, md.value))
        print("---------------------------------------------")

        newmd = { 'testkey': '88', 'testkey2': '99', 'A': '1', 'a': 'lower1' }

        ihelper.put_metaf(self.irff_m13, newmd, absolute=True)

        irmd = ihelper.get_metaf(self.irff_m13, absolute=True)
        for md in irmd:
            print("{}={}".format(md.keyword, md.value))
        assert len(irmd) >= len(newmd)


    def test_remove_metaf (self):
        ihelper = IRodsHelper(self.defargs)
        assert ihelper is not None

        irff = ihelper.getf(self.irff_m13, absolute=True)
        assert irff is not None

        for md in ihelper.get_metaf(self.irff_m13, absolute=True):
            print("{}={}".format(md.keyword, md.value))
        print("---------------------------------------------")

        oldmd = { 'testkey': '88', 'testkey2': '99', 'A': '1', 'a': 'lower1' }

        ihelper.remove_metaf(self.irff_m13, oldmd, absolute=True)

        irmd = ihelper.get_metaf(self.irff_m13, absolute=True)
        for md in irmd:
            print("{}={}".format(md.keyword, md.value))
        assert len(irmd) <= len(irmd) + len(oldmd)
