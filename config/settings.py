# Path to the root location of the application. When app is run inside
# a container (the default) this is container-relative (e.g. '/imdtk')
APP_ROOT = '/imdtk'

# Configuration directory, inside the application
CONFIG_DIR = "{}/config".format(APP_ROOT)

# iRods configuration directory, inside the application
IRODS_DIR = "{}/.irods".format(APP_ROOT)

# Default resource file for catalog field aliases.
DEFAULT_CAT_ALIASES_FILEPATH = "{}/jwst-cat-aliases.ini".format(CONFIG_DIR)

# Default resource file for image header keyword aliases.
DEFAULT_IMD_ALIASES_FILEPATH = "{}/jwst-imd-aliases.ini".format(CONFIG_DIR)

# Default config file for database configuration.
DEFAULT_DBCONFIG_FILEPATH = "{}/jwst-dbconfig.ini".format(CONFIG_DIR)

# Default resource file for default field values.
DEFAULT_FIELDS_FILEPATH = "{}/jwst-fields.toml".format(CONFIG_DIR)

# Default schema and table name in which to store image metadata in a database.
DEFAULT_METADATA_TABLE_NAME = 'jwst'

# Default hybrid schema and table name in which to store image metadata in a database.
DEFAULT_HYBRID_TABLE_NAME = 'hybrid'

# Logging level
LOG_LEVEL = 'INFO'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

# Image and Cutout Server information
IMAGE_FETCH_PREFIX = 'https://hector.cyverse.org/cuts/img/fetch_by_filepath?path='

# Name of this program: used programmatically so keeping it lower case.
PROGRAM_NAME = 'imdtk'

# Set of possible field names which will contain declination values:
DEC_ALIASES = [ 'DEC', 'dec', 's_dec' ]

# Set of possible field names which will contain unique ID values:
ID_ALIASES = [ 'ID', 'id', 's_obs_id', 'galaxy_id' ]

# Set of possible field names which will contain right ascension values:
RA_ALIASES = [ 'RA', 'ra', 's_ra' ]

# List of required SQL fields in the hybrid PG/JSON database table (excluding JSON fields):
SQL_FIELDS_HYBRID = [ 'md5sum', 's_dec', 's_ra', 'is_public', 'obs_collection' ]

# Work directory: the mount point in the container for file input and output.
WORK_DIR = '/work'
