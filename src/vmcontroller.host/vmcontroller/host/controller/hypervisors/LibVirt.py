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
    from vmcontroller.common import support, exceptions
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

WAITING_GRACE_MS = 800

logger = logging.getLogger(__name__)

######### PUBLIC API #########

def version():
    def impl():
        return "LibVirt-" + libvirt.getVersion()
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
        dom = conn.lookupByName(vm)
        return dom.undefine()
    d = threads.deferToThread( impl )
    return d

def start(vm, guiMode):
    def impl():
        dom = conn.lookupByName(vm)
        return dom.create()
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    return d

def shutdown(vm):
    def impl():
        dom = conn.lookupByName(vm)
        return dom.shutdown()
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def reset(vm):
    def impl():
        dom = conn.lookupByName(vm)
        return dom.reboot(True)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def powerOff(vm):
    def impl():
        dom = conn.lookupByName(vm)
        return dom.destroy()
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def pause(vm): 
    def impl():
        dom = conn.lookupByName(vm)
        return dom.suspend()
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def resume(vm):
    def impl():
        dom = conn.lookupByName(vm)
        return dom.resume()
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
        dom = conn.lookupByName(vm)
        return dom.save("Current")
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
        return conn.listDefinedDomains()
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

def listVMsWithState():
    def impl():
        pass # ? over list of domains, use dom.isActive()?
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


######### INITIALIZATION #########

hypervisor = "vbox"
conn = None

if hypervisor == "vbox":
    conn = libvirt.open('vbox:///session')

if conn == None:
    logger.fatal("Failed to open connection to the hypervisor")
    sys.exit(1)

logger.info("Using LibVirt %s and Hypervisor: %s. VMs found: %s" % (libvirt.getVersion(), hypervisor, conn.listDefinedDomains()))

