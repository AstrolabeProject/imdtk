# Configuration information
CONFIG_DIR = '/imdtk/config'

# Default resource file for header keyword aliases.
DEFAULT_ALIASES_FILEPATH = "{}/jwst-aliases.ini".format(CONFIG_DIR)

# Default resource file for default field values.
DEFAULT_FIELDS_FILEPATH = "{}/jwst-fields.toml".format(CONFIG_DIR)

# Logging level
LOG_LEVEL = 'INFO'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

# Image and Cutout Server information
IMAGES_DIR = '/vos'
IMAGE_FETCH_PREFIX = 'https://hector.cyverse.org/cuts/image_fetch?path='

# Work directory: the mount point in the container for file input and output.
WORK_DIR = '/work'

# Name of this program: used programmatically so keeping it lower case.
PROGRAM_NAME = 'imdtk'

# Resource information (currently unused)
# RESOURCE_PKG = 'imdtk.resources'
