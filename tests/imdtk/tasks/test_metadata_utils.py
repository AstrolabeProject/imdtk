# Tests for the metata utilities module.
#   Written by: Tom Hicks. 7/16/2020.
#   Last Modified: Update for is_public boolean.
#
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
            "is_public": False,
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
            "is_public": False
        }
    }

    cat_md = {
        "column_info": {
            "name": [
                "ID",
                "RA",
                "DEC",
                "redshift",
                "x",
                "y",
                "a",
                "b",
                "kron_flag"
            ],
            "format": [
                "K",
                "D",
                "D",
                "D",
                "D",
                "D",
                "D",
                "D",
                "K"
            ]
        },
        "aliased": [
            "id",
            "s_ra",
            "s_dec",
        ],
        "data": [
            [ 100, 53.199042819, -27.853734606, 2.2401, 1.968, 2.032,
              1.908737, 1.794, 2.267, 1.645, 2.636, 0.211,
              2.94, 9.0, 1.21917, 2.053, 0.977, 1.7755 ],
            [ 200, 53.202861572, -27.852506463, 2.4176, 3.785, 4.943,
              0.7698837, 2.118, 7.504, 0.771, 9.485, 0.219,
              12.567, 9.0, 16.0073, 4.809, 0.979, 6.9545 ]
        ]
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


    def test_get_aliased_column_names (self):
        data = utils.get_aliased_column_names(self.cat_md)
        print(data)
        assert data is not None
        assert len(data) > 1
        assert 'id' in data
        assert 's_ra' in data
        assert 's_dec' in data

        assert 'ID' not in data
        assert 'RA' not in data
        assert 'DEC' not in data
        assert 'COMMENT' not in data
        assert 'name' not in data
        assert 'kron_flag' not in data


    def test_get_column_names (self):
        data = utils.get_column_names(self.cat_md)
        print(data)
        assert data is not None
        assert len(data) > 1
        assert 'ID' in data
        assert 'RA' in data
        assert 'DEC' in data
        assert 'kron_flag' in data
        assert 'COMMENT' not in data
        assert 'name' not in data


    def test_get_column_formats (self):
        data = utils.get_column_formats(self.cat_md)
        print(data)
        assert data is not None
        assert len(data) > 1
        assert 'K' in data
        assert 'D' in data
        assert 'C' not in data
        assert 'Q' not in data


    def test_get_data (self):
        data = utils.get_data(self.cat_md)
        print(data)
        assert data is not None
        assert len(data) == 2
        assert data[0][0] == 100
        assert data[0][5] == 2.032
        assert data[0][17] == 1.7755
        assert data[1][0] == 200
        assert data[1][5] == 4.943
        assert data[1][17] == 6.9545
