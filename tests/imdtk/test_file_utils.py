# Tests for the file utilities module.
#   Written by: Tom Hicks. 5/22/2020.
#   Last Modified: Add tests for filename_core and full_path.
#
import imdtk.core.file_utils as utils

import os
import pytest
from pathlib import Path


class TestFileUtils(object):

    tmpPath = '/tmp'
    dirPath = '/tmp/MadeUpDIR'
    dirLink = '/tmp/linkToMadeUpDIR'
    fylPath = '/tmp/HiGhLy_UnLiKeLy'
    fylLink = '/tmp/linkToHiGhLy_UnLiKeLy'


    def test_filename_core(self):
        assert utils.filename_core(None) == ''
        assert utils.filename_core('') == ''
        assert utils.filename_core('/tmp') == 'tmp'
        assert utils.filename_core('/tmp/somefile') == 'somefile'
        assert utils.filename_core('/tmp/somefile.py') == 'somefile'


    def test_full_path(self):
        assert utils.full_path('~') == '/root'
        assert utils.full_path('~/.bashrc') == '/root/.bashrc'
        assert utils.full_path('/tmp') == '/tmp'
        assert utils.full_path('/tmp/somefile') == '/tmp/somefile'
        assert utils.full_path('/tmp/somefile.py') == '/tmp/somefile.py'


    def test_gen_file_paths(self):
        paths = [ p for p in utils.gen_file_paths(os.getcwd()) ]
        assert len(paths) != 0, "The generated path list for PWD is not empty."

        paths = [ p for p in utils.gen_file_paths(self.fylPath) ]
        assert len(paths) == 0, "The generated path list for non-existant directory is empty."


    def test_good_dir_path(self):
        # also tests is_readable
        assert utils.good_dir_path('dummy') == False
        assert utils.good_dir_path(self.fylPath) == False
        assert utils.good_dir_path(self.dirPath) == False

        assert utils.good_dir_path('.') == True
        assert utils.good_dir_path('/') == True
        assert utils.good_dir_path('/tmp') == True

        # setup directories and links
        os.mkdir(self.dirPath, mode=0o444)
        dirp = Path(self.dirPath)
        dlnk = Path(self.dirLink)
        dlnk.symlink_to(dirp)

        assert utils.good_dir_path(self.dirPath) == True
        assert utils.good_dir_path(self.dirLink) == True

        # cleanup directories and links
        os.rmdir(self.dirPath)
        os.remove(self.dirLink)


    def test_good_dir_path_write(self):
        # also tests is_writable
        assert utils.good_dir_path('dummy', True) == False
        assert utils.good_dir_path(self.fylPath, True) == False
        assert utils.good_dir_path(self.dirPath, True) == False

        assert utils.good_dir_path('.', True) == True
        assert utils.good_dir_path('/', True) == True
        assert utils.good_dir_path('/tmp', True) == True

        # setup directories and links
        os.mkdir(self.dirPath, mode=0o555)
        dirp = Path(self.dirPath)
        dlnk = Path(self.dirLink)
        dlnk.symlink_to(dirp)

        assert utils.good_dir_path(self.dirPath) == True
        assert utils.good_dir_path(self.dirPath, True) == True
        assert utils.good_dir_path(self.dirLink) == True
        assert utils.good_dir_path(self.dirLink, True) == True

        # cleanup directories and links
        os.rmdir(self.dirPath)
        os.remove(self.dirLink)


    def test_good_file_path(self):
        # also tests is_readable
        assert utils.good_file_path('.') == False
        assert utils.good_file_path('/') == False
        assert utils.good_file_path('/tmp') == False
        assert utils.good_file_path('dummy') == False
        assert utils.good_file_path('/dummy') == False
        assert utils.good_file_path('/images/JADES/NONE.fits') == False

        # setup files and links
        fylp = Path(self.fylPath)
        fylp.touch(mode=0o444)
        flnk = Path(self.fylLink)
        flnk.symlink_to(fylp)               # ln -s fylPath fylLink

        assert utils.good_file_path(self.fylPath) == True
        assert utils.good_file_path(self.fylLink) == True

        # cleanup directories and links
        os.remove(self.fylPath)
        os.remove(self.fylLink)


    def test_good_file_path_write(self):
        # also tests is_writable
        assert utils.good_file_path('.', True) == False
        assert utils.good_file_path('/', True) == False
        assert utils.good_file_path('/tmp', True) == False
        assert utils.good_file_path('dummy') == False
        assert utils.good_file_path(self.fylPath) == False
        assert utils.good_file_path(self.fylLink) == False

        # setup files and links
        fylp = Path(self.fylPath)
        fylp.touch(mode=0o444)
        flnk = Path(self.fylLink)
        flnk.symlink_to(fylp)               # ln -s fylPath fylLink

        assert utils.good_file_path(self.fylPath) == True
        assert utils.good_file_path(self.fylLink) == True

        # cleanup directories and links
        os.remove(self.fylPath)
        os.remove(self.fylLink)


    def test_is_acceptable_filename(self):
        FITS_EXTS = ['.fits', '.fits.gz']
        assert utils.is_acceptable_filename('.fits', FITS_EXTS) == True
        assert utils.is_acceptable_filename('.fits.fits', FITS_EXTS) == True
        assert utils.is_acceptable_filename('x.fits', FITS_EXTS) == True
        assert utils.is_acceptable_filename('X.Y.fits', FITS_EXTS) == True
        assert utils.is_acceptable_filename('XXX-YYY_.fits', FITS_EXTS) == True
        assert utils.is_acceptable_filename('.fits.gz', FITS_EXTS) == True
        assert utils.is_acceptable_filename('.fits.fits.gz', FITS_EXTS) == True
        assert utils.is_acceptable_filename('x.fits.gz', FITS_EXTS) == True
        assert utils.is_acceptable_filename('X.Y.fits.gz', FITS_EXTS) == True
        assert utils.is_acceptable_filename('XXX-YYY_.fits.gz', FITS_EXTS) == True

        assert utils.is_acceptable_filename('.', FITS_EXTS) == False
        assert utils.is_acceptable_filename('.fitsy', FITS_EXTS) == False
        assert utils.is_acceptable_filename('.fits.fitsy', FITS_EXTS) == False
        assert utils.is_acceptable_filename('fits', FITS_EXTS) == False
        assert utils.is_acceptable_filename('fits.gz', FITS_EXTS) == False
        assert utils.is_acceptable_filename('X.fit', FITS_EXTS) == False
        assert utils.is_acceptable_filename('X.fitsgz', FITS_EXTS) == False
        assert utils.is_acceptable_filename('bad.fits_gz', FITS_EXTS) == False
        assert utils.is_acceptable_filename('yyy.exe', FITS_EXTS) == False
        assert utils.is_acceptable_filename('YYY.EXE', FITS_EXTS) == False
        assert utils.is_acceptable_filename('BAD.ONE', FITS_EXTS) == False
        assert utils.is_acceptable_filename('BAD.ONE.gz', FITS_EXTS) == False


    def test_path_has_dots(self):
        assert utils.path_has_dots('.') == True
        assert utils.path_has_dots('..') == True
        assert utils.path_has_dots('./..') == True
        assert utils.path_has_dots('./usr/dummy/') == True
        assert utils.path_has_dots('../usr/dummy/') == True
        assert utils.path_has_dots('/usr/dummy/./smarty') == True
        assert utils.path_has_dots('/usr/dummy/../smarty') == True
        assert utils.path_has_dots('/usr/dummy/.') == True
        assert utils.path_has_dots('/usr/dummy/..') == True

        assert utils.path_has_dots(None) == False
        assert utils.path_has_dots('') == False
        assert utils.path_has_dots('dummy') == False
        assert utils.path_has_dots('dummy.txt') == False
        assert utils.path_has_dots('dummy.file.txt') == False
        assert utils.path_has_dots('/') == False
        assert utils.path_has_dots('/dummy') == False
        assert utils.path_has_dots('/usr/dummy') == False
        assert utils.path_has_dots('/usr/dummy/') == False


    def test_validate_path_strings(self):
        FILE_EXTENTS = ['.txt']
        testpaths = [ '.', '/', '/NoSuch',
                      '/tmp', '/tmp/NoSuch', '/work',
                      '/imdtk/tests/resources/empty.txt',
                      '/imdtk/tests/resources/m13.fits',
                      '/images/JADES/NONE.fits',
                      '', None ]
        pathlst = utils.validate_path_strings(testpaths, FILE_EXTENTS)
        print("PATHLIST={}".format(pathlst))
        assert len(pathlst) == 5
        assert '/tmp' in pathlst
        assert '/work' in pathlst
        assert '/imdtk/tests/resources/empty.txt' in pathlst
        assert '/imdtk/tests/resources/m13.fits' not in pathlst
        assert '/images/JADES/NONE.fits' not in pathlst


    def test_validate_path_strings_fits(self):
        FITS_EXTENTS = ['.fits', '.fits.gz']
        testpaths = [ '.', '/', '/NoSuch',
                      '/tmp', '/tmp/NoSuch', '/work',
                      '/imdtk/tests/resources/empty.txt',
                      '/imdtk/tests/resources/m13.fits',
                      '/images/JADES/NONE.fits',
                      '', None ]
        pathlst = utils.validate_path_strings(testpaths, FITS_EXTENTS)
        print("PATHLIST={}".format(pathlst))
        assert len(pathlst) == 5
        assert '/tmp' in pathlst
        assert '/work' in pathlst
        assert '/imdtk/tests/resources/m13.fits' in pathlst
        assert '/images/JADES/NONE.fits' not in pathlst
        assert '/imdtk/tests/resources/empty.txt' not in pathlst
