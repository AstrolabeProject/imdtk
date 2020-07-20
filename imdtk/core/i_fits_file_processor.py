#
# Abstract class defining the interface that all Processor classes must implement.
#   Written by: Tom Hicks. 4/4/2020.
#   Last Modified: Revamp error handling.
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



    def get_obs_core_key_from_alias (self, hdr_key):
        """ Return the ObsCore keyword for the given FITS header keyword, or None if not found. """
        return self._fits_aliases.get(hdr_key)


    def load_db_configuration (self, db_config_file):
        """ Load database configuration parameters from the given DB config filepath. """
        if (self._DEBUG):
            print("(IFitsFileProcessor.load_db_configuration): Loading from DB config file '{}'".format(db_config_file))

        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(db_config_file)
        db_config = config['db_properties']

        if (self._DEBUG):
            print("(IFitsFileProcessor.load_db_configuration): Read {} DB configuration properties.".format(len(db_config)))

        return dict(db_config)


    def load_aliases (self, alias_file):
        """ Load field name aliases from the given alias filepath. """
        if (self._DEBUG):
            print("(IFitsFileProcessor.load_aliases): Loading from aliases file '{}'".format(alias_file))

        config = configparser.ConfigParser(strict=False, empty_lines_in_values=False)
        config.optionxform = lambda option: option
        config.read(alias_file)
        aliases = config['aliases']

        if (self._DEBUG):
            print("(IFitsFileProcessor.load_aliases): Read {} field name aliases.".format(len(aliases)))

        return dict(aliases)
