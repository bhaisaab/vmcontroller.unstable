#!/usr/bin/python
#
# This file contains parts of code taken from VBox SDK samples:
# Copyright (C) 2009-2010 Oracle Corporation,
# part of VirtualBox Open Source Edition (OSE), as
# available from http://www.virtualbox.org. This file is free software;
# you can redistribute it and/or modify it under the terms of the GNU
# General Public License (GPL) as published by the Free Software
# Foundation, in version 2 as it comes in the "COPYING" file of the
# VirtualBox OSE distribution. VirtualBox OSE is distributed in the
# hope that it will be useful, but WITHOUT ANY WARRANTY of any kind.
#

try:
    import logging
    import os
    import platform
    import sys
    import uuid
    import pdb

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
        return ctx['vb'].version
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

def createVM(name):
    vb = ctx['vb']
    def impl():
        ms = getMachines()
        for m in ms:
            if m.name == name:
              raise ValueError("VM '%s' already exists" % name)
        guestType = vb.getGuestOSType('Linux26')
        mach = vb.createMachine("", name, guestType.id, "", True)
        mach.saveSettings()
        vb.registerMachine( mach )
        logger.debug("Created VM with UUID %s" % mach.id)
        return (True, name)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def openVM(vmFile):
    vb = ctx['vb']
    def impl():
        mach = vb.openMachine(vmFile) # Overwrite is true
        vb.registerMachine( mach )
        logger.debug("Created VM %s with UUID %s" % (mach.name, mach.id))
        return (True, mach.name)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def removeVM(vm):
    def impl():
        mgr = ctx['mgr']
        vb = ctx['vb']
        mach = machById(vm)
        id = mach.id
        name = mach.name
        logger.debug("Removing VM: %s with UUID %s " % (mach.name, id))
        cmdClosedVm(mach, detachVmDevice, ["ALL"])
        mach = mach.unregister(ctx['global'].constants.CleanupMode_Full)
        if mach:
             mach.deleteSettings()
        return (True, name)
    d = threads.deferToThread( impl )
    return d

def startVM(vm, guiMode):
    if platform.system() != "Windows":
        def impl():
            mgr = ctx['mgr']
            vb = ctx['vb']
            perf = ctx['perf']
            mach = machById(vm)
            session = mgr.getSessionObject(vb)
            logger.info("Starting VM for machine %s" % mach.name)
            if guiMode:
                progress = mach.launchVMProcess(session, "gui", "")
            else:
                progress = mach.launchVMProcess(session, "vrdp", "")                

            while not progress.completed:
                logger.debug("Loading VM %s - %s %%" % (mach.name, str(progress.percent)))
                progress.waitForCompletion(WAITING_GRACE_MS)
            if progress.completed and int(progress.resultCode) == 0:
                logger.info("Startup of machine %s completed: %s" % (mach.name, str(progress.completed)))
                if perf:
                    try:
                        perf.setup(['*'], [mach], 10, 15)
                    except Exception,e:
                        logger.error("Error occured %s" % e)
                 # if session not opened, close doesn't make sense
                session.unlockMachine()
            else:
                reportError(progress)
                return False
            return True 

        d = threads.deferToThread(impl)
    else:
        m = findMachineByNameOrId(vm)
        mName = str(m.name)
        processProtocol = VBoxHeadlessProcessProtocol()
        pseudoCWD = os.path.dirname(sys.modules[__name__].__file__)
        vboxBinariesPath = None #TODO: use VBOX_INSTALL_PATH
        cmdWithPath = os.path.join(pseudoCWD, 'scripts', 'vboxstart.bat')
        cmdWithArgs = ("vboxstart.bat", vboxBinariesPath, mName)
        cmdPath = os.path.join(pseudoCWD, 'scripts')
        newProc = lambda: reactor.spawnProcess( processProtocol, cmdWithPath, args=cmdWithArgs, env=None, path=cmdPath )
        reactor.callWhenRunning(newProc)
        d = True #in order to have a unique return 
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    return d

def shutdown(vm):
    def impl():
        return cmdExistingVm(vm, 'shutdown', None)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def reset(vm):
    def impl():
        return cmdExistingVm(vm, 'reset', None)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def powerDown(vm):
    def impl():
        return cmdExistingVm(vm, 'powerdown', None)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def pause(vm): 
    def impl():
        return cmdExistingVm(vm, 'pause', None)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def resume(vm):
    def impl():
        return cmdExistingVm(vm, 'resume', None)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def getState( vm): 
    def impl():
        m = machById(vm)
        mstate = m.state
        stateName = getNameForMachineStateCode(mstate)
        return stateName
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl) 
    return d

def saveState(vm):
    def impl():
        return cmdExistingVm(vm, 'saveState', None)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def discardState(vm):
    def impl():
        return cmdExistingVm(vm, 'discardState', None)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

def listVMs():
    def impl():
        vb = ctx['vb']
        ms = getMachines()
        msNames = [ str(m.name) for m in ms ]
        return msNames
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

def listVMsWithState():
    def impl():
        vb = ctx['vb']
        ms = getMachines()
        msNamesAndStates = [ (str(m.name), getNameForMachineStateCode(m.state)) \
            for m in ms ]
        return dict(msNamesAndStates)
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

def listRunningVMs():
    def impl():
        vb = ctx['vb']
        ms = getMachines()
        isRunning = lambda m: m.state ==  ctx['const'].MachineState_Running
        res = filter( isRunning, ms )
        res = [ str(m.name) for m in res ]
        return res
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

####### TODO

def takeSnapshot(vm, name, desc):
    def impl():
        return _execProgressCmd(vm, 'takeSnapshot', (name, desc))

    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

#TODO: Read and see docs from ISnapshot, give snapshot as arg
def restoreSnapshot(vm, name, desc=""):
    def impl():
        return _execProgressCmd(vm, 'restoreSnapshot', (name, desc))

    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

#FIXME: ID from Name
def deleteSnapshot(vm, name):
    snapshotId = getNamesToIdsMapping().get(name)
    logger.debug("Deleting snapshot named '%s' with Id: %s" % (name, snapshotId) )
    def impl():
        return _execProgressCmd(vm, 'deleteSnapshot', (snapshotId))

    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread( impl )
    return d

######### Internal Helpers #########

def reportError(progress):
    ei = progress.errorInfo
    if ei:
        logger.error("Error in %s: %s" %(ei.component, ei.text) )

def getMachines():
    if ctx['vb'] is not None:
        return ctx['global'].getArray(ctx['vb'], 'machines')

def findMachineByNameOrId(vm):
    for m in getMachines():
        if (m.name == vm) or (m.id == vm):
            res = m
            break
        else: #only reached if "break" never exec'd
            raise Exceptions.NoSuchVirtualMachine(str(vm))
    return res 

def getSessionForVm(vm):
    vb = ctx['vb']
    mgr = ctx['mgr']
    session = mgr.getSessionObject(vb)
    m = findMachineByNameOrId(vm) 
    try:
        vb.openExistingSession(session, m.id)
    except:
        vb.openSession(session, m.id)
    return session

def machById(id):
    try:
        mach = ctx['vb'].getMachine(id)
    except:
        mach = ctx['vb'].findMachine(id)
    return mach

def detachVmDevice(mach,args):
    atts = ctx['global'].getArray(mach, 'mediumAttachments')
    hid = args[0]
    for a in atts:
        if a.medium:
            if hid == "ALL" or a.medium.id == hid:
                mach.detachDevice(a.controller, a.port, a.device)

def detachMedium(mid,medium):
    cmdClosedVm(machById(mid), detachVmDevice, [medium])

def cmdClosedVm(mach, cmd, args=[], save=True):
    session = ctx['global'].openMachineSession(mach, True)
    mach = session.machine
    try:
        cmd(mach, args)
    except Exception, e:
        save = False
        logger.error("Error: %s" % e)
    if save:
        try:
            mach.saveSettings()
        except Exception, e:
            logger.error("Error: %s" % e)
    ctx['global'].closeMachineSession(session)

def cmdExistingVm(vm,cmd,args):
    session = None
    mach = machById(vm)
    try:
        vb = ctx['vb']
        session = ctx['mgr'].getSessionObject(vb)
        mach.lockMachine(session, ctx['global'].constants.LockType_Shared)
    except Exception,e:
        logger.error(ctx, "Session to '%s' not open: %s" % (mach.name,str(e)))
        return
    if session.state != ctx['const'].SessionState_Locked:
        logger.info("Session to '%s' in wrong state: %s" % (mach.name, session.state))
        session.unlockMachine()
        return

    console=session.console
    ops={'pause':           lambda: console.pause(),
         'resume':          lambda: console.resume(),
         'start':           lambda: console.powerUp(),
         'shutdown':        lambda: console.powerButton(),
         'powerdown':       lambda: console.powerDown(),
         'reset':           lambda: console.reset(),
         'saveState':       lambda: console.saveState(),
         'discardState':    lambda: console.discardSavedState(True), # True: Saved state file is deleted

         #FIXME:
         'takeSnapshot':    lambda: console.takeSnapshot(args[0], args[1]) ,
         'restoreSnapshot': lambda: console.restoreSnapshot(),
         'deleteSnapshot':  lambda: console.deleteSnapshot(args[0]),
         'stats':           lambda: perfStats(mach),
         'guest':           lambda: guestExec(mach, console, args),
         'ginfo':           lambda: ginfo(console, args),
         'guestlambda':     lambda: args[0](mach, console, args[1:]),
         'gueststats':      lambda: guestStats(console, args),
         }
    try:
        progress = ops[cmd]()
        if progress:
            while not progress.completed:
                logger.debug("Command progress - %s %%" % str(progress.percent))
                progress.waitForCompletion(WAITING_GRACE_MS)
            if progress.completed and int(progress.resultCode) == 0:
                logger.info("Execution of command '%s' on VM %s completed" % (cmd, mach.name))
            else:
                session.unlockMachine()
                reportError(progress)
                return False
    except Exception, e:
        logger.error("Problem while running cmd '%s': %s" % (cmd, str(e)) )
    
    session.unlockMachine()
    return True

def getNamesToIdsMapping(): 
    macToName = _getMACToNameMapping()
    nameToMac = support.reverseDict(macToName)
    return nameToMac

def getIdsToNamesMapping():
    macToName = _getMACToNameMapping()
    return macToName

def getPerformanceData(vm):
    def impl():
        return ctx['perf'].query( ["*"], [vm] )
      
    logger.debug("Controller method %s invoked" % support.discoverCaller() )
    d = threads.deferToThread(impl)
    return d

def _getMACToNameMapping():
  vb = ctx['vb']
  def numsToColonNotation(nums):
    nums = str(nums)
    #gotta insert a : every two number, except for the last group.
    g = ( nums[i:i+2] for i in xrange(0, len(nums), 2) )
    return ':'.join(g)

  ms = getMachines()
  entriesGen = ( ( numsToColonNotation(m.getNetworkAdapter(1).MACAddress), str(m.name) ) 
      for m in getMachines() ) 
  #entriesGen = ( ( m.getNetworkAdapter(1).MACAddress, str(m.name) ) for m in _getMachines() )

  mapping = dict(entriesGen)
  return mapping

def getNameForMachineStateCode(c):
  d = ctx['const']._Values['MachineState']
  revD = [k for (k,v) in d.iteritems() if v == c]
  return revD[0]

class _VBoxHeadlessProcessProtocol(protocol.ProcessProtocol):
  logger = logging.getLogger( support.discoverCaller() )

  def connectionMade(self):
    self.transport.closeStdin()
    self.logger.debug("VBoxHeadless process started!")
  def outReceived(self, data):
    self.logger.debug("VBoxHeadless stdout: %s" % data)
  def errReceived(self, data):
    self.logger.debug("VBoxHeadless stderr: %s" % data)
  def inConnectionLost(self):
    pass #we don't care about stdin. We do in fact close it ourselves
  def outConnectionLost(self):
    self.logger.info("VBoxHeadless closed its stdout")
  def errConnectionLost(self):
    self.logger.info("VBoxHeadless closed its stderr")
  def processExited(self, reason):
    #This is called when the child process has been reaped 
    pass
  def processEnded(self, reason):
    #This is called when all the file descriptors associated with the child
    #process have been closed and the process has been reaped
    self.logger.warn("Process ended (code: %s) " % reason.value.exitCode)

############ INITIALIZATION ######################

from vboxapi import VirtualBoxManager

g_virtualBoxManager = VirtualBoxManager(None, None)
ctx = {'global':g_virtualBoxManager,
       'mgr':g_virtualBoxManager.mgr,
       'vb':g_virtualBoxManager.vbox,
       'const':g_virtualBoxManager.constants,
       }
ctx['perf'] = ctx['global'].getPerfCollector(ctx['vb'])
