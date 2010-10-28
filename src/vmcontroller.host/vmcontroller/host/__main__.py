#!python
"""
VMController Host - a general purpose host-side virtual machine controller.
"""

import os
import sys
import logging
import warnings
import inject

from pkg_resources import resource_stream
from ConfigParser import SafeConfigParser
from optparse import OptionParser

from vmcontroller.host.config import *

logger = lambda: logging.getLogger(__name__)

def init_logging(logfile=None, loglevel=logging.INFO):
    format = '%(asctime)s [%(threadName)s] - %(name)s - %(levelname)s - %(message)s'
    if logfile:
        logging.basicConfig(filename=logfile, level=loglevel, format=format)
    else:
        logging.basicConfig(level=loglevel, format=format)

def init():
    config = init_config()

    injector = inject.Injector()
    inject.register(injector)
    injector.bind('config', to=config)
    injector.bind('logger', to=logger)

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="configfile",
                      help="Read configuration from FILE. (Overrides default config file.)", metavar="FILE")
    parser.add_option("-a", "--host", dest="xmlrpc_host",
                      help="Listen on specified address for XMLRPC interface (default 127.0.0.1)", metavar="ADDR")
    parser.add_option("-p", "--port", dest="xmlrpc_port",
                      help="Listen on specified port for XMLRPC interface (default 50505)", type="int", metavar="PORT")
    parser.add_option("-l", "--logfile", dest="logfile",
                      help="Log to specified file.", metavar="FILE")
    parser.add_option("--debug", action="store_true", dest="debug", default=False, 
                      help="Sets logging to debug (unless logging configured in config file).")

    (options, args) = parser.parse_args()

    init_config_file(options.configfile)

    if options.xmlrpc_host is not None:
        config.set('xmlrpc', 'host', options.xmlrpc_host)
        
    if options.xmlrpc_port is not None:
        config.set('xmlrpc', 'port', str(options.xmlrpc_port))

    level = logging.DEBUG if options.debug else logging.INFO
    init_logging(logfile=options.logfile, loglevel=level)
    debug_config()

def main():
    init()
    logger().info("Welcome to VMController Host!")

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception, e:
        logger().error("Server terminated due to error: %s" % e)
        logger().exception(e)
