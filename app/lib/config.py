import os
import yaml

PORTAL_CONFIG = os.path.join(os.path.dirname(__file__), '../../configs/configs.yml')
CONFIG = yaml.load(file(PORTAL_CONFIG, 'r'))
