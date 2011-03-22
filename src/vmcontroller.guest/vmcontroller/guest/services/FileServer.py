try:
    import os
    import logging

    from twisted.internet import reactor, protocol, ssl
    from twisted.protocols import basic

    from vmcontroller.common.FileTransfer import *
    from vmcontroller.common import support, exceptions
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

class FileTransferProtocol(basic.LineReceiver):
    delimiter = '\n'
    logger = logging.getLogger(support.discoverCaller())

    def connectionMade(self):
        self.factory.clients.append(self)
        self.file_handler = None
        self.file_data = ()

        self.transport.write('VMController Guest File Server\n')
        self.transport.write('ENDMSG\n')

        self.logger.debug('Connection from: %s (%d clients total)' % (self.transport.getPeer().host, len(self.factory.clients)))
	
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        self.file_handler = None
        self.file_data = ()

        self.logger.debug('Connection from %s lost (%d clients left)' % (self.transport.getPeer().host, len(self.factory.clients)))

    def lineReceived(self, line):
        self.logger.debug('Received the following line from the client [%s]: %s' % (self.transport.getPeer().host, line))
        data = self._cleanAndSplitInput(line)
        if len(data) == 0 or data == '':
            return

        command = data[0].lower()
        if not command in COMMANDS:
            self.transport.write('Invalid command\n')
            self.transport.write('ENDMSG\n')
            return
        if command == 'list':
            if len(data) < 2:
                data.append(self.factory.files_path)
            self._send_list_of_files(data[1])
        elif command == 'get':
            try:
                filename = data[1]
            except IndexError:
                self.transport.write('Missing filename\n')
                self.transport.write('ENDMSG\n')
                return

            if not os.path.exists(filename):
                    self.transport.write('File with filename %s does not exist, please give full path\n' % (filename))
                    self.transport.write('ENDMSG\n')
                    return

            file_size = os.path.getsize(filename)
            md5_hash = get_file_md5_hash(filename)
            self.logger.debug('Sending file: %s (%d KB)' % (filename, file_size / 1024))

            self.transport.write('HASH %s %s\n' % (os.path.basename(filename), md5_hash))
            self.setRawMode()

            try:
              for bytes in read_bytes_from_file(filename):
                  self.transport.write(bytes)
            except:
              self.logger.debug("File sending failed")	
            self.transport.write('\r\n')	
            self.setLineMode()
        elif command == 'put':
	          try:
		            filename = data[1]
		            file_hash = data[2]
	          except IndexError:
		            self.transport.write('Missing filename or file MD5 hash\n')
		            self.transport.write('ENDMSG\n')
		            return

	          self.file_data = (filename, file_hash)
	
	          # Switch to the raw mode (for receiving binary data)
	          self.logger.debug('Receiving file: %s' % filename)
	          self.setRawMode()
        elif command == 'help':
	          self.transport.write('Available commands:\n\n')
	
	          for key, value in COMMANDS.iteritems():
		            self.transport.write('%s - %s\n' % (value[0], value[1]))
	
	          self.transport.write('ENDMSG\n')				
        elif command == 'quit':
	          self.transport.loseConnection()
		
    def rawDataReceived(self, data):
	      filename = self.file_data[0]
	      file_path = os.path.join(self.factory.files_path, filename)
	
	      self.logger.debug('Receiving file chunk (%d KB)' % (len(data)))
	
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
			          self.transport.write('Got: %s\n' % filename)
			          self.transport.write('ENDMSG\n')
			
			          self.logger.debug('File %s has been successfully transfered' % filename)
		        else:
			          os.unlink(file_path)
			          self.transport.write('File was successfully transfered but not saved, due to invalid MD5 hash\n')
			          self.transport.write('ENDMSG\n')
		
			          self.logger.debug('File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename))
	      else:
		        self.file_handler.write(data)
	
    def _send_list_of_files(self, path=""):
	      files = os.listdir(path)

	      self.transport.write('Found [%d] files in the path (%s): \n\n' % (len(files), path))	
	      for filename in files:
		        self.transport.write('- %s (%d.2 KB)\n' % (filename, (os.path.getsize(filename) / 1024.0)))
		
	      self.transport.write('ENDMSG\n')
		
    def _cleanAndSplitInput(self, input):
	      input = input.strip()
	      input = input.split(' ')

	      return input

class FileServerFactory(protocol.ServerFactory):
    protocol = FileTransferProtocol

    def __init__(self, files_path):
        self.files_path = files_path
        self.clients = []
        self.files = None

if __name__ == '__main__':
    port = 1234
    path = "/tmp"

    reactor.listenSSL(port, FileServerFactory(path), 
            ssl.DefaultOpenSSLContextFactory('privkey.pem', 'cacert.pem'))
    reactor.run()
