#!python
import inject
import logging

from twisted.trial import unittest
from ConfigParser import SafeConfigParser
from vmcontroller.host.config import *

# Rather simple config test

class TestHostConfig(unittest.TestCase):
    def setUp(self):
        self.config = init_config()

    def test_config(self):
        self.assertEquals( self.config.get("host", "network_interface"), "vboxnet0")
        self.assertEquals( self.config.get("xmlrpc", "host"), "127.0.0.1")
        self.assertEquals( int(self.config.get("xmlrpc", "port")), 50505)
        self.assertEquals( self.config.get("broker", "host"), "0.0.0.0")
        self.assertEquals( self.config.get("hypervisor", "name"), "VirtualBox")
