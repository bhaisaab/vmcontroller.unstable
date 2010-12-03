import os
import optparse
import logging

from twisted.internet import reactor, protocol, stdio, defer
from twisted.protocols import basic
from twisted.internet.protocol import ClientFactory

from vmcontroller.common.FileTransfer import COMMANDS, display_message, validate_file_md5_hash, get_file_md5_hash, read_bytes_from_file, clean_and_split_input

class FileTransfer(basic.LineReceiver):
    delimiter = '\n'
    
    def __init__(self, server_ip, server_port, files_path):
        self.isConnected = False;
        self.server_ip = server_ip
        self.server_port = server_port
        self.files_path = files_path
        self.logger = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))  
        self.factory = FileTransferClientFactory(self.files_path)
        self.connection = reactor.connectTCP(self.server_ip, self.server_port, self.factory)
        self.factory.deferred.addCallback(self._display_response)

    def sendFile(self, file_path, filename):
        if not os.path.isfile(file_path):
            self.logger.debug('This file does not exist')
            return

        file_size = os.path.getsize(file_path) / 1024
        
        print 'Uploading file: %s->%s (%d KB)' % (file_path, filename, file_size)
        
        self.connection.transport.write('PUT %s %s\n' % (filename, get_file_md5_hash(file_path)))
        self.setRawMode()
        
        for bytes in read_bytes_from_file(file_path):
            self.connection.transport.write(bytes)
        
        self.connection.transport.write('\r\n')
        self.factory.deferred.addCallback(self._display_response)


        
    def _sendCommand(self, line):
        """ Sends a command to the server. """
        print "Command:", line

        data = clean_and_split_input(line) 
        if len(data) == 0 or data == '':
            return 

        command = data[0].lower()
        if not command in COMMANDS:
            self.self.logger.debug('Invalid command')
            return
        
        if command == 'list' or command == 'help' or command == 'quit':
            self.connection.transport.write('%s\n' % (command))
        elif command == 'get':
            try:
                filename = data[1]
            except IndexError:
                self.logger.debug('Missing filename')
                return
            
            self.connection.transport.write('%s %s\n' % (command, filename))
        elif command == 'put':
            try:
                file_path = data[1]
                filename = data[2]
            except IndexError:
                self.logger.debug('Missing local file path or remote file name')
                return
            
            if not os.path.isfile(file_path):
                self.logger.debug('This file does not exist')
                return

            file_size = os.path.getsize(file_path) / 1024
            
            print 'Uploading file: %s->%s (%d KB)' % (file_path, filename, file_size)
            
            self.connection.transport.write('PUT %s %s\n' % (filename, get_file_md5_hash(file_path)))
            self.setRawMode()
            
            for bytes in read_bytes_from_file(file_path):
                self.connection.transport.write(bytes)
            
            self.connection.transport.write('\r\n')   
            
            # When the transfer is finished, we go back to the line mode 
            self.setLineMode()
        else:
            self.connection.transport.write('%s %s\n' % (command, data[1]))

        self.factory.deferred.addCallback(self._display_response)
        
    def _display_response(self, lines = None):
        """ Displays a server response. """
        
        if lines:
            for line in lines:
                print '%s' % (line)
        self.transport.write('> ')
        self.connection.transport.write('list\n')
        self.isConnected = True;
        self.factory.deferred = defer.Deferred()
        
   

class FileTransferProtocol(basic.LineReceiver):
    delimiter = '\n'

    def connectionMade(self):
        self.buffer = []
        self.file_handler = None
        self.file_data = ()
        
        print 'Connected to the server'
        
    def connectionLost(self, reason):
        self.file_handler = None
        self.file_data = ()
        
        print 'Connection to the server has been lost'
        #reactor.stop()
    
    def lineReceived(self, line):
        if line == 'ENDMSG':
            self.factory.deferred.callback(self.buffer)
            self.buffer = []
        elif line.startswith('HASH'):
            # Received a file name and hash, server is sending us a file
            data = clean_and_split_input(line)

            filename = data[1]
            file_hash = data[2]
            
            self.file_data = (filename, file_hash)
            self.setRawMode()
        else:
            self.buffer.append(line)
        
    def rawDataReceived(self, data):
        filename = self.file_data[0]
        file_path = os.path.join(self.factory.files_path, filename)
        
        print 'Receiving file chunk (%d KB)' % (len(data))
        
        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')
            
        if data.endswith('\r\n'):
            # Last chunk
            data = data[:-2]
            self.file_handler.write(data)
            self.setLineMode()
            
            self.file_handler.close()
            self.file_handler = None
            
            if validate_file_md5_hash(file_path, self.file_data[1]):
                print 'File %s has been successfully transfered and saved' % (filename)
            else:
                os.unlink(file_path)
                print 'File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename)
        else:
            self.file_handler.write(data)

class FileTransferClientFactory(protocol.ClientFactory):
    protocol = FileTransferProtocol
    
    def __init__(self, files_path):
        self.files_path = files_path
        self.deferred = defer.Deferred()

if __name__ == '__main__':

    vmIp = "192.168.56.101"
    # FIXME Get these stuff automatically
    fileDirPath = '/home/rohit/temp'
    fileServerPort = 1234

    fileUtil = FileTransfer(vmIp, fileServerPort, fileDirPath)

    pathToLocalFileName = '/home/rohit/tetris.py'
    pathToRemoteFileName = 'tetris.txt'
    print "Transferring file: %s to VM(%s)" % (pathToLocalFileName, vmIp)

    reactor.callLater(5, fileUtil.sendFile, pathToLocalFileName, pathToRemoteFileName)
    #fileUtil.sendFile(pathToLocalFileName, pathToRemoteFileName)
#    fileUtil.sendFile(pathToLocalFileName, pathToRemoteFileName)
#    stdio.StandardIO(CommandLineProtocol(IP, PORT, LOCALPATH))
    reactor.run()
