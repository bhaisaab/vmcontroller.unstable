#!/usr/bin/python
# LibVirt.py: A general toolkit to support multiple hypervisors
# such as Xen, KVM, VirtualBox and VMWare.
# Python bindings to use: libvirt-python on RHEL/Fedora, python-libvirt on Ubuntu. 

try:
    import logging
    import os
    import platform
    import sys
    import uuid

    import libvirt

    from twisted.internet import protocol, reactor, defer, threads
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

WAITING_GRACE_MS = 800

logger = logging.getLogger(__name__)

######### INITIALIZATION #########

conn = libvirt.openReadOnly(None)
if conn == None:
    logger.fatal("Failed to open connection to the hypervisor")
    sys.exit(1)

try:
    dom0 = conn.lookupByName("Domain-0")
except:
    print 'Failed to find the main domain'
    sys.exit(1)

# right now works only with qemu, for evey hypervisor, a driver is needed
print "Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType())
print dom0.info()

######### PUBLIC API #########

def version():
    def impl():
        return libvirt.getVersion()
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

def createVM(xmlFile):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def removeVM(vm):
    def impl():
        pass
    d = threads.deferToThread( impl )
    return d

def start(vm, guiMode):
    def impl():
        pass 
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    return d

def shutdown(vm):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def reset(vm):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def powerOff(vm):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def pause(vm): 
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def resume(vm):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def states():
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl) 
    return d

def getState( vm): 
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl) 
    return d

def saveState(vm):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def discardState(vm):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def listVMs():
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

def listVMsWithState():
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

def listRunningVMs():
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

def listSnapshots(vm):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

def takeSnapshot(vm, name, desc):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def restoreSnapshot(vm, name):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def deleteSnapshot(vm, name):
    def impl():
        pass
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

