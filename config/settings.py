# Path to the root location of the application. If app is run
# inside a container (the default) this is container-relative (e.g. '/imdtk')
APP_ROOT = '/imdtk'

# Configuration information
CONFIG_DIR = "{}/config".format(APP_ROOT)

# Default resource file for header keyword aliases.
DEFAULT_ALIASES_FILEPATH = "{}/jwst-aliases.ini".format(CONFIG_DIR)

# Default config file for database configuration.
DEFAULT_DBCONFIG_FILEPATH = "{}/jwst-dbconfig.ini".format(CONFIG_DIR)

# Default resource file for default field values.
DEFAULT_FIELDS_FILEPATH = "{}/jwst-fields.toml".format(CONFIG_DIR)

# Default schema and table name in which to store image metadata in a database.
DEFAULT_METADATA_TABLE_NAME = 'sia.jwst'

# Default hybrid schema and table name in which to store image metadata in a database.
DEFAULT_HYBRID_TABLE_NAME = 'sia.hybrid'

# Logging level
LOG_LEVEL = 'INFO'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

# Image and Cutout Server information
IMAGES_DIR = '/vos'
IMAGE_FETCH_PREFIX = 'https://hector.cyverse.org/cuts/image_fetch?path='

# Name of this program: used programmatically so keeping it lower case.
PROGRAM_NAME = 'imdtk'

# Resource information (currently unused)
# RESOURCE_PKG = 'imdtk.resources'

# List of required SQL fields in the hybrid PG/JSON database table (excluding JSON fields):
SQL_FIELDS_HYBRID = [ 's_dec', 's_ra', 'obs_collection', 'is_public' ]

# Path to the tests directory.
TEST_DIR = "{}/tests".format(APP_ROOT)

# Work directory: the mount point in the container for file input and output.
WORK_DIR = '/work'
