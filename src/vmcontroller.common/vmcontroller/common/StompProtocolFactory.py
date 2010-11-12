import logging
import pdb 

try:
    import inject
    import stomper
    from twisted.internet.protocol import ReconnectingClientFactory
    from twisted.internet import reactor
except ImportError, e:
    print "Import Error: %s" % e
    exit()

from vmcontroller.common import support, exceptions

class StompProtocolFactory(ReconnectingClientFactory):
    """ Responsible for creating an instance of L{StompProtocol} """

    logger = logging.getLogger( support.discoverCaller() )

    __stompProtocol = inject.attr('stompProtocol')
    initialDelay = delay = 5.0
    factor = 1.0
    jitter = 0.0

    def __init__(self):
        #retry every 5 seconds, with no back-off
        self.protocol = lambda: self.__stompProtocol #sigh... self.protocol must be callable

    def clientConnectionLost(self, connector, reason):
        self.logger.info("Connection with the broker lost: %s" % reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        self.logger.error("Connection with the broker failed: %s" % reason )
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)



