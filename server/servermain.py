from twisted.application import service, internet
from twisted.internet import reactor

from core.config import loadConfig, errors
from core.core import ChatFactory

config = loadConfig("server.conf", "conf")
if not config:
    print "Errors encountered in config:"
    for error in errors:
        print "\t" + error

state = {
    "config": config,
}

application = service.Application("supportserver")
factory = ChatFactory(state)
port = config["general"]["port"]
serv = internet.TCPServer(int(port), factory)
serv.setServiceParent(application)
serv.startService()
reactor.run()
