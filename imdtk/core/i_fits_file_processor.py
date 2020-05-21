#
# Abstract class defining the interface that all Processor classes must implement.
#   Written by: Tom Hicks. 4/4/2020.
#   Last Modified: Move string to value to metadata fields class.
#
import abc
import configparser

import imdtk.core.fits_utils as fits_utils

class IFitsFileProcessor (abc.ABC):

    # Keys to be ignored when reading FITS file header.
    FITS_IGNORE_KEYS = [ 'COMMENT', 'HISTORY', '' ]  # empty key important: removes non-Key/Value entries


    @abc.abstractmethod
    def cleanup (self):
        """ Do any cleanup/shutdown tasks necessary for the processor instance. """
        pass


    @abc.abstractmethod
    def process_a_file (self, apath):
        """ Process the single given FITS image file. """
        pass



    def filter_header_fields (self, header_fields, ignore=None):
        """
        Remove any entries whose keys are in the ignore list from the given header fields dictionary.
        If not given, the ignore list defaults to the value of the FITS_IGNORE_KEYS class variable.
        """
        if (ignore is None):
            ignore = self.FITS_IGNORE_KEYS
        for key in ignore:
            header_fields.pop(key, None)    # remove keyed entry: ignore key errors


    def get_obs_core_key_from_alias (self, hdr_key):
        """ Return the ObsCore keyword for the given FITS header keyword, or None if not found. """
        return self._fits_aliases.get(hdr_key)


    def load_db_configuration (self, db_config_file):
        """ Load database configuration parameters from the given DB config filepath. """
        if (self._VERBOSE):
            print("(IFitsFileProcessor.load_db_configuration): Loading from DB config file '{}'".format(db_config_file))

        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(db_config_file)
        db_config = config['db_properties']

        if (self._VERBOSE):
            print("(IFitsFileProcessor.load_db_configuration): Read {} DB configuration properties.".format(len(db_config)))

        return dict(db_config)


    def load_aliases (self, alias_file):
        """ Load field name aliases from the given alias filepath. """
        if (self._VERBOSE):
            print("(IFitsFileProcessor.load_aliases): Loading from aliases file '{}'".format(alias_file))

        config = configparser.ConfigParser(strict=False, empty_lines_in_values=False)
        config.optionxform = lambda option: option
        config.read(alias_file)
        aliases = config['aliases']

        if (self._VERBOSE):
            print("(IFitsFileProcessor.load_aliases): Read {} field name aliases.".format(len(aliases)))

        return dict(aliases)
