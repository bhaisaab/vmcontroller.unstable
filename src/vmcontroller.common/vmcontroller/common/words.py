import CommandExecuter
from vmcontroller.common import support

import logging
import time 
import stomper 
import fnmatch

logger = logging.getLogger( support.discoverCaller() )

CMD_REQ_DESTINATION="/topic/vmcontroller_requests"
CMD_RES_DESTINATION="/topic/vmcontroller_responses"
CONN_DESTINATION="/topic/vmcontroller_connections"

class BaseWord(object):
  """ Initializes the Frame object with the inheriting class' name """
  def __init__(self, src, dst):
    """
    @param invoker instance of the element (host, vm) receiving/sending the word.
    """
    self._frame = stomper.Frame()
    self._frame.body = self.__name__
    headers = {}
    headers['from'] = src
    headers['to'] = dst
    headers['timestamp'] = str(time.time())
    self._frame.headers = headers
    self._frame.cmd = 'SEND'

   

