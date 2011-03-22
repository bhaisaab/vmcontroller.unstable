import xmlrpclib
from optparse import OptionParser

host = 'http://localhost'
port = ':50505'
p = xmlrpclib.ServerProxy(host+port)

parser = OptionParser()
(options, args) = parser.parse_args()

funcArgs = ""
argc = len(args[1:])
for c in range(argc):
    if c != 0:
        funcArgs += ', '
    funcArgs += args[c+1]

print "Executing: ", 'vmcontroller.host:' + args[0] + '('+ funcArgs + ')'
print eval('p.' + args[0] + '(' + funcArgs + ')')
