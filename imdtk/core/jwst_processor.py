#
# Class which implements the interface for processing JWST FITS file images.
#   Written by: Tom Hicks. 4/4/2020.
#   Last Modified: Import/use config directory from settings.
#
import os
import sys
import configparser
from astropy.io import fits

import imdtk.core.fits_utils as fits_utils
from config.settings import CONFIG_DIR
from imdtk.core.fields_info_factory import FieldsInfoFactory
from imdtk.core.information_outputter import InformationOutputter
from imdtk.core.i_fits_file_processor import IFitsFileProcessor
from imdtk.core.metadata_fields import MetadataFields


class JwstProcessor (IFitsFileProcessor, MetadataFields):

    # Processor-specific list of column names in the header field information file.
    FIELD_INFO_COLUMN_NAMES = [ 'obsCoreKey', 'datatype', 'required', 'default' ]

    # Default resource file for header keyword aliases.
    DEFAULT_ALIASES_FILEPATH = "{}/jwst-aliases.ini".format(CONFIG_DIR)

    # Default configuration file for database connection information.
    DEFAULT_DBCONFIG_FILEPATH = "{}/jwst-dbconfig.ini".format(CONFIG_DIR)

    # Default resource file for header field information.
    DEFAULT_FIELDS_FILEPATH = "{}/jwst-fields.txt".format(CONFIG_DIR)

    # Spatial resolutions for NIRCam filters, keyed by filter name.
    FILTER_RESOLUTIONS = {
        'F070W': 0.030, 'F090W': 0.034,  'F115W': 0.040,  'F140M': 0.048, 'F150W': 0.050,
        'F162M': 0.055, 'F164N': 0.056,  'F150W2': 0.046, 'F182M': 0.062, 'F187N': 0.064,
        'F200W': 0.066, 'F210M': 0.071,  'F212N': 0.072,  'F250M': 0.084, 'F277W': 0.091,
        'F300M': 0.100, 'F322W2': 0.097, 'F323N': 0.108,  'F335M': 0.111, 'F356W': 0.115,
        'F360M': 0.120, 'F405N': 0.136,  'F410M': 0.137,  'F430M': 0.145, 'F444W': 0.145,
        'F460M': 0.155, 'F466N': 0.158,  'F470N': 0.160,  'F480M': 0.162
    }

    # Schema and table name in which to store image metadata in the database.
    METADATA_TABLE_NAME = 'sia.jwst'


    def __init__(self, args):
        """ Constructor for the JWST-specific FITS file processor class. """

        # Dictionary of arguments from the command line processor
        self._args = args

        # Verbose setting: when true, show extra information about program operation.
        self._VERBOSE = self._args.get('verbose', False)

        # Debug setting: when true, show internal information for debugging.
        self._DEBUG = self._args.get('debug', False)

        # Mappping of FITS header keywords to ObsCore keywords.
        # Read from a given external file or a default internal resource file.
        self._fits_aliases = None

        # The wrapper instance for the FITS file currently being processed.
        self._fits_file = None

        # An instance of IInformationOutputter for outputting the processed information.
        self._info_outputter = None

        # An instance of the field information factory.
        self._fields_info_factory = None


        # load the FITS field name aliases from a given file path or a default resource path
        alias_file = self._args.get('alias_file') or self.DEFAULT_ALIASES_FILEPATH
        self._fits_aliases = self.load_aliases(alias_file)
        if (self._DEBUG):
            for k, v in self._fits_aliases.items():
                print("{}={}".format(k, v))

        # load the database configuration from a given file path or a default resource path
        db_config_file = self._args.get('db_config_file') or self.DEFAULT_DBCONFIG_FILEPATH
        if (not db_config_file):
            errMsg = '(jwst_processor.ctor): Database parameters file missing.'
            raise RuntimeError(errMsg)

        db_config = self.load_db_configuration(db_config_file)
        if (not db_config):
            errMsg = '(jwst_processor.ctor): No database parameters read from database configuration file.'
            raise RuntimeError(errMsg)

        if (self._DEBUG):
            print("(jwst_processor.ctor): db_config: {}".format(db_config))

        # add some processor-specific settings to the configuration arguments
        args[ 'db_config'] = db_config
        args[ 'field_info_column_names'] = self.FIELD_INFO_COLUMN_NAMES
        if (not self._args.get('fields_file')):
            args['fields_file'] = self.DEFAULT_FIELDS_FILEPATH

        # instantiate an instance of InformationOutputter or raise exception if unable to do so
        args['metadata_table_name'] = self.METADATA_TABLE_NAME  # pass JWST-specific table name
        try:
            self._info_outputter = InformationOutputter(args)
        except Exception as ex:
            errMsg = "(jwst_processor.ctor): Unable to create an InformationOutputter from this configuration: {}".format(args)
            raise RuntimeError(errMsg)

        # instantiate a factory to load field information
        try:
            self._fields_info_factory = FieldsInfoFactory(args)
        except Exception as ex:
            errMsg = "(jwst_processor.ctor): Unable to create a FieldsInfoFactory from this configuration: {}".format(args)
            raise RuntimeError(errMsg)

        if (args.get('debug')):
            print("(jwst_processor.ctor): args={}".format(args))



    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for the processor instance. """
        if (self._DEBUG):
            print("(jwst_processor.cleanup): Cleanup called.")
        self._info_outputter.cleanup()      # cleanup child information outputter instance


    def process_a_file (self, fpath):
        """ Process the single given FITS image file. """
        if (self._VERBOSE):
            print("(jwst_processor.process_a_file): Processing FITS file '{}'".format(fpath))

        try:
            with fits.open(fpath) as ff_hdus_list:
                if (fits_utils.is_catalog_file(ff_hdus_list)):
                    if (self._VERBOSE):
                        print("(jwst_processor.process_a_file): Skipping FITS catalog '{}'".format(fpath))
                        return 0            # exit out now
                return self.process_an_image_file(fpath, ff_hdus_list)

        except OSError as oserr:
            if (self._DEBUG):
                errMsg = "(jwst_processor.process_a_file): ERROR: {}".format(repr(oserr))
                print(errMsg)
            if (self._VERBOSE):
                errMsg = "(jwst_processor.process_a_file): Unable to read file '{}' as a FITS file. File skipped.".format(fpath)
                print(errMsg)
                return 0


    def calc_spatial_resolution (self, fields_info):
        """
        Use the filter value to determine the spatial resolution based on a NIRCam
        filter-resolution table.
        """
        filt = fields_info.get_value_for('filter')
        if (filt):
            resolution = self.FILTER_RESOLUTIONS.get(filt)
            field_info = fields_info.get('s_resolution')
            if (resolution and (field_info is not None)):
                field_info.set_value(resolution)


    def process_an_image_file (self, file_path, ff_hdus_list):
        """ Process the single given FITS image file. """
        if (self._DEBUG):
            print("(jwst_processor.process_an_image_file): Processing FITS file '{}'".format(file_path))
            print("(jwst_processor.process_an_image_file): HDUs list = '{}'".format(ff_hdus_list))

        # make a map of all FITS headers and value strings
        header_fields = fits_utils.get_header_fields(ff_hdus_list) # defaults to first HDU
        if (header_fields is None):          # if unable to read the FITS file headers
            if (self._DEBUG):
                errMsg = "Unable to read FITS file '{}' headers. File skipped.".format(file_path)
                log.error('JwstProcessor.processAnImageFile', errMsg)
            return 0                        # then skip this file

        # filter out any header fields with keys in the ignore list
        self.filter_header_fields(header_fields)

        if (self._DEBUG):
            print("(jwst_processor.process_an_image_file): Read and kept {} FITS metadata fields:".format(len(header_fields)))
            for k, v in header_fields.items():
                print("{}={} {}".format(k, v, type(v)))

        # parse the WCS information from the FITS image file
        wcs_info = fits_utils.get_WCS(ff_hdus_list)  # defaults to first HDU

        # Data structure defining information for fields processed by this processor.
        # Loads the field information from the file previously given to the constructor.
        # NOTE: need to reread this info for each input file as it will be mutated each time.
        fields_info = self._fields_info_factory.load_fields_info()

        # add information about the input file that is being processed
        self.add_file_information(file_path, fields_info)

        try:
            # calculate the scale for each image
            self.calc_scale(wcs_info, fields_info)

            # add header field keys and string values from the FITS file
            self.add_info_from_fits_headers(header_fields, fields_info)

            # convert the header field string values, where possible
            self.convert_header_values(fields_info)

            # add defaults for missing values, if possible
            self.add_default_values_for_fields(fields_info)

            # calculate the image corners and spatial limits
            #   self.calc_corners(header_fields, fields_info)
            self.calc_corners(wcs_info, fields_info)

            # try to compute values for computable fields which are still missing values
            self.compute_values_for_fields(wcs_info, header_fields, fields_info)

            # do some checks for required fields
            self.ensure_required_fields(fields_info)

            # output the extracted field information
            self._info_outputter.output_image_info(fields_info)

            # print(fields_info)              # DEBUGGING


        except Exception as ex:
            errMsg = "(jwst_processor.process_an_image_file): Failed to process file '{}'. Error message was:\n{}".format(file_path, ex)
            raise RuntimeError(errMsg)

        return 1
