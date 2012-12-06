import os
from ConfigParser import SafeConfigParser


ebaysuds_config = SafeConfigParser()
ebaysuds_config.read(os.environ.get('EBAYSUDS_CONFIG_PATH', os.path.abspath('ebaysuds.conf')))
