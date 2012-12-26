import os
from ConfigParser import SafeConfigParser

CONFIG_PATH = os.environ.get('EBAYSUDS_CONFIG_PATH', os.path.abspath('ebaysuds.conf'))

ebaysuds_config = SafeConfigParser()
ebaysuds_config.read(CONFIG_PATH)
