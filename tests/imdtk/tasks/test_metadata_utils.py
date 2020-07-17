# Tests for the metata utilities module.
#   Written by: Tom Hicks. 7/16/2020.
#   Last Modified: Correct the class name.
#
import pytest

import imdtk.tasks.metadata_utils as utils


class TestMetadataUtils(object):

    metadata = {
        "file_info": {
            "file_name": "F356W.fits",
            "file_path": "/images/DC_191217/F356W.fits",
            "file_size": 337230720
        },
        "headers": {
            "SIMPLE": True,
            "BITPIX": -64,
            "NAXIS": 2,
            "NAXIS1": 9791,
            "NAXIS2": 4305,
            "DATE": "2019-12-14T21:10:36.490",
            "TIMESYS": "UTC",
            "WCSAXES": 2,
            "CRVAL1": 53.157662568,
            "CRVAL2": -27.8075199236
        },
        "aliased": {
            "im_naxes": 2,
            "s_xel1": 9791,
            "s_xel2": 4305,
            "gmt_date": "2019-12-14T21:10:36.490",
            "radesys": "FK5",
            "filter": "F356W",
            "t_exptime": 1374.3053,
            "t_min": 58831.88236678241,
            "t_max": 58831.89827309352,
            "equinox": 2000.0
        },
        "fields_info": {
            "target_name": { "required": True },
            "obs_collection": { "required": True, "default": "JWST" },
            "equinox": { "required": False, "default": 2000.0 },
            "radesys": { "required": False, "default": "ICRS" },
            "gmt_date": { "required": False }
        },
        "defaults": {
            "dataproduct_type": "image",
            "calib_level": 3,
            "obs_publisher_did": "ivo://astrolabe.arizona.edu/jwst",
            "access_format": "application/fits",
            "obs_creator_name": "JWST",
            "im_naxes": 2,
            "im_nsubarrays": 1,
            "is_public": 0,
            "equinox": 2000.0,
            "radesys": "ICRS"
        },
        "calculated": {
            "im_scale": 8.806000000000108e-06,
            "im_naxes": 2,
            "s_xel1": 9791,
            "s_xel2": 4305,
            "gmt_date": "2019-12-14T21:10:36.490",
            "equinox": 2000.0,
            "dataproduct_type": "image",
            "s_ra": 53.157662568,
            "s_dec": -27.8075199236,
            "is_public": 0
        }
    }


    def test_get_aliased (self):
        data = utils.get_aliased(self.metadata)
        print(data)
        assert data is not None
        assert len(data) > 1
        assert 'radesys' in data
        assert 'equinox' in data
        assert 'COMMENT' not in data


    def test_get_calculated (self):
        data = utils.get_calculated(self.metadata)
        print(data)
        assert data is not None
        assert len(data) > 1
        assert 's_ra' in data
        assert 'equinox' in data
        assert 'COMMENT' not in data


    def test_get_defaults (self):
        data = utils.get_defaults(self.metadata)
        print(data)
        assert data is not None
        assert len(data) > 1
        assert 'is_public' in data
        assert 'equinox' in data
        assert 'COMMENT' not in data


    def test_get_fields_info (self):
        data = utils.get_fields_info(self.metadata)
        print(data)
        assert data is not None
        assert len(data) > 1
        assert 'target_name' in data
        assert 'equinox' in data
        assert 'COMMENT' not in data


    def test_get_file_info (self):
        data = utils.get_file_info(self.metadata)
        print(data)
        assert data is not None
        assert len(data) > 1
        assert 'file_name' in data
        assert 'file_size' in data
        assert 'equinox' not in data
        assert 'COMMENT' not in data


    def test_get_headers (self):
        data = utils.get_headers(self.metadata)
        print(data)
        assert data is not None
        assert len(data) > 1
        assert 'SIMPLE' in data
        assert 'NAXIS' in data
        assert 'COMMENT' not in data
