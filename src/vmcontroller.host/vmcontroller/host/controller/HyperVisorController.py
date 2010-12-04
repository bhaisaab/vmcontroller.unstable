"""
Instantiates the apropriate controller.

It follows the naming convention defined by appending 
the hypervisor name, as gotten from the provided configuration, 
with "Controller". Such a class must be exist and be accesible.

Note that if the controller class resides in a different package,
its name must include the package name as well.
"""

try:
    import logging
    import inject

    from twisted.internet import defer
    from vmcontroller.common import support, exceptions
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

CONTROLLERS_PATH = "hypervisors" #relative to this file

logger = logging.getLogger( support.discoverCaller() )

@inject.param('config')
def _createController(config):
    """
    Creates the appropriate (hypervisor) controller based on the
    given configuration. 

    This is the place where to perform particular initialization tasks for 
    the particular hypervisor controller implementations.

    @param config: an instance of L{ConfigParser}
    """
    hv = config.get('hypervisor', 'name')
    hvMod = None
    logger.debug("Hypervisor specified in config: '%s'" % hv)
    fqHvName = "%s.%s" % (CONTROLLERS_PATH, hv)
  
    try:
        hvPkg = __import__(fqHvName, globals=globals(), level=-1)
        hvMod = getattr(hvPkg, hv)
    except ImportError, e:
        msg = "Hypervisor '%s' is not supported. Error: %s" % (hv, e)
        logger.fatal(msg)
        raise exceptions.ConfigError(msg)

    logger.info("Using %s as the HyperVisor" % hvMod.__name__)

    return hvMod 

_controller = None
def getController():
    global _controller
    if not _controller:
        _controller = _createController()

    return _controller

def createVM(vm, image):
    """
    Creates virtual machine with given parameters.
    @param vm: Virtual machine's name.
    @param image: Path to the virtual machine's image
    """
    return defer.maybeDeferred( getController().createVM, vm, image )

def removeVM(vm):
    """
    Removes virtual machine. NOTE: This operation is undo-able.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().removeVM, vm)

def start(vm):
    """
    Starts virtual machine.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().start, vm )

def shutdown(vm):
    """
    Shutdown virtual machine.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().shutdown, vm )

def sleep(vm):
    """
    Sends ACPI sleep signal to virtual machine.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().sleep, vm )

def reset(vm):
    """
    Sends ACPI power reset signal to virtual machine.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().reset, vm )

def powerOff(vm):
    """
    Turn off virtual machine, without a proper shutdown.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().powerOff, vm )

def pause(vm): 
    """
    Pauses running virtual machine.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().pause, vm )

def resume(vm):
    """
    Resumes a paused virtual machine.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().resume, vm )

def getState(vm):
    """
    Returns state of a virtual machine.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().getState, vm )

def saveState(vm):
    """
    Saves state of the virtual machine.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().saveState, vm )

def discardState(vm):
    """
    Discards any saved state of the virtual machine.
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().discardState, vm )

def takeSnapshot(vm, name, desc = ""):
    """
    Saves snapshot of current virtual machines vm state.
    @param vm: Virtual machine's name.
    @param name: Name of the snapshot.
    @param desc: Snapshot's description.
    """
    return defer.maybeDeferred( getController().takeSnapshot, vm, name, desc )

#FIXME: Restore last saved snapshot only
def restoreSnapshot(vm, name, desc = ""):
    """
    Restores snapshot
    @param vm: Virtual machine's name.
    """
    return defer.maybeDeferred( getController().restoreSnapshot, vm, name, desc )

#FIXME: some gid err
def deleteSnapshot(vm, name):
    """
    Saves snapshot of current virtual machines vm state.
    @param vm: Virtual machine's name.
    @param name: Name of the snapshot.
    """
    return defer.maybeDeferred( getController().deleteSnapshot, vm, name )

def listVMs():
    """listVMs()"""
    return defer.maybeDeferred( getController().listVMs )

def listVMsWithState():
    """listVMsWithState()"""
    return defer.maybeDeferred( getController().listVMsWithState )

def listRunningVMs():
    """listRunningVMs()"""
    return defer.maybeDeferred( getController().listRunningVMs )

def getNamesToIdsMapping():
    """getNamesToIdsMapping"""
    return defer.maybeDeferred( getController().getNamesToIdsMapping )

def getIdsToNamesMapping(): 
    """getIdsToNamesMapping"""
    return defer.maybeDeferred( getController().getIdsToNamesMapping )

def getPerformanceData(vm):
    """getPerformanceData(vm)"""
    return defer.maybeDeferred( getController().getPerformanceData, vm)


