#!python
"""
VMController Host - a general purpose host-side virtual machine controller.
"""

import os
import sys
import logging
import warnings
import multiprocessing
import time

try:
    import inject
    from twisted.internet import reactor
except ImportError, e:
    print "Import Error: %s" % e
    exit()

from pkg_resources import resource_stream
from ConfigParser import SafeConfigParser
from optparse import OptionParser
from vmcontroller.host.config import *

logger = logging.getLogger(__name__)

def start_coilmq(config, server_event, tries=-1, delay=1, backoff=1.5):
    m_tries = tries
    m_delay = delay
    m_server = None

    try:
        from coilmq.config import config as broker_config
        import coilmq.start
    except ImportError, e:
        print "Import error: %s\nPlease check." % e
        exit()

    if config.has_section('broker'):
        for (attribute, value) in config.items('broker'):
            if attribute != 'name':
                broker_config.set('coilmq', attribute, value)
                logger.debug("[coilmq] %s = %s" % (attribute, value))

    broker_server = None
    while True:
        try:
            broker_server = coilmq.start.server_from_config(broker_config)
            logger.info("Stomp server listening on %s:%s" % broker_server.server_address)
            server_event.set()
            broker_server.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Stomp server stopped by user interrupt.")
            raise SystemExit()
        except IOError as ex:
            logger.error("Exception while starting coilmq broker: '%s'", ex)
            if m_tries != 0: 
                logger.debug("Retrying coilmq startup in %.1f seconds...", m_delay)
                time.sleep(m_delay)
                m_delay *= backoff
                m_tries -= 1
            else:
                logger.debug("Ran out of trials (tried %d times) for coilmq startup. Giving up.", tries)
                break
        except Exception, e:
            logger.error("Stomp server stopped due to error: %s" % e)
            logger.exception(e)
            raise SystemExit()
        finally:
            if broker_server: broker_server.server_close()

@inject.param('config')
def use_coilmq(config, brokerTimeout=60):
    manager = multiprocessing.Manager()
    server_event = manager.Event()
    broker = multiprocessing.Process(target=start_coilmq, args=(config, server_event))
    broker.daemon = False
    broker.name = 'VMController-Broker'
    broker.start()

    server_event.wait(brokerTimeout)
    if not server_event.is_set():
        logger.fatal("Broker not available after %.1f seconds. Giving up", brokerTimeout)
        return -1

@inject.param('config')
def use_morbid(config):
    try:
        import morbid
    except ImportError, e:
        print "Import error: %s\nPlease check." % e
        exit()

    morbid_factory = morbid.StompFactory(verbose=True)
    broker_host = config.get('broker', 'host')
    broker_port = int(config.get('broker', 'port'))
    logger.info("Starting MorbidQ broker %s:%s", broker_host, broker_port)
    reactor.listenTCP(broker_port, morbid_factory, interface=broker_host)

@inject.param('config')
def start(config, brokerTimeout = 5.0):
    broker_name = config.get('broker', 'name')

    if broker_name == 'morbid':
        use_morbid()
    elif broker_name == 'coilmq':
        use_coilmq()
    else:
        logger.fatal("No broker found... Exiting")
        exit()

    reactor.run()

def init_logging(logfile=None, loglevel=logging.INFO):
    format = '%(asctime)s - [%(threadName)s] %(filename)s:%(lineno)s - (%(levelname)s) %(message)s'
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

    debug_config(config)

def main():
    init()
    logger.info("Welcome to VMController Host!")
    start()

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception, e:
        logger.error("Server terminated due to error: %s" % e)
        logger.exception(e)
