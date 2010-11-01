"""
Configuration support functionality.

"""

import os
import logging

try:
    import inject
except ImportError as e:
    print "Import Error: %s" % e
    exit()

from ConfigParser import SafeConfigParser
from pkg_resources import resource_stream

@inject.param('config')
def init_config_file(config_file, config):
    if config_file and os.path.exists(config_file):
        read = config.read([config_file])
        if not read:
            raise ValueError("Could not read configuration from file: %s" % config_file)

def init_config():
    config = SafeConfigParser()
    config.readfp(resource_stream(__name__, 'default.cfg'))
    return config

@inject.param('logger')
def debug_config(config, logger):
    for section in config.sections():
        for option in config.options(section):
            logger.debug("[%s] %s=%s" % (section, option, config.get(section, option)))
