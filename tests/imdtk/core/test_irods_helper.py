# Tests for the iRods interface module.
#   Written by: Tom Hicks. 10/20/20.
#   Last Modified: Add test for to_dirpath.
#
import os
import pytest

import imdtk.exceptions as errors
import imdtk.core.irods_helper as irh

from config.settings import DEFAULT_IRODS_AUTH_FILEPATH, DEFAULT_IRODS_ENV_FILEPATH

class TestIRodsHelper(object):

    def test_create_helper_noconn (self):
        args = {}
        ihelper = irh.IRodsHelper(args, connect=False)
        print(ihelper)
        assert ihelper is not None


    def test_create_helper_noargs (self):
        args = {}
        ihelper = irh.IRodsHelper(args)
        print(ihelper)
        assert ihelper is not None


    def test_get_authentication_file (self):
        args = {}
        ihelper = irh.IRodsHelper(args, connect=False)
        print(ihelper)
        assert ihelper is not None

        auth_file = ihelper.get_authentication_file(args)
        print(auth_file)
        assert auth_file is not None
        assert auth_file == DEFAULT_IRODS_AUTH_FILEPATH


    def test_get_environment_file (self):
        args = {}
        ihelper = irh.IRodsHelper(args, connect=False)
        print(ihelper)
        assert ihelper is not None

        env_file = ihelper.get_environment_file(args)
        print(env_file)
        assert env_file is not None
        assert env_file == DEFAULT_IRODS_ENV_FILEPATH


    def test_to_dirpath (self):
        args = {}
        ihelper = irh.IRodsHelper(args, connect=False)

        ihelper.to_dirpath('/') == '/'
        ihelper.to_dirpath('.') == './'
        ihelper.to_dirpath('x') == 'x/'
        ihelper.to_dirpath('x/') == 'x/'
        ihelper.to_dirpath('abc') == 'abc/'
        ihelper.to_dirpath('abc/') == 'abc/'
        ihelper.to_dirpath('/a/b/c') == '/a/b/c/'
        ihelper.to_dirpath('/a/b/c/') == '/a/b/c/'
