import time
import pdb
import logging

try:
    import inject
    import stomper
except ImportError, e:
    print "Import Error: %s" % e
    exit()

from vmcontroller.common import BaseStompEngine 
from vmcontroller.common import support, exceptions 
from vmcontroller.common import destinations

#@inject.appscope
class HostStompEngine(BaseStompEngine):
  
  logger = logging.getLogger(support.discoverCaller())

  def __init__(self):
    super( HostStompEngine, self ).__init__()

  def connected(self, msg):
    #once connected, subscribe
    return ( stomper.subscribe(destinations.CONN_DESTINATION), 
             stomper.subscribe(destinations.CMD_RES_DESTINATION) )


