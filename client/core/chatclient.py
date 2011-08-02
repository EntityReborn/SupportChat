import traceback
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import connectionDone, ReconnectingClientFactory

from hooks import Hookable

from protocolapi import API

class BadMessage(Exception): pass

class Client(LineReceiver):
    def parsemsg(self, s):
        if not s:
            raise BadMessage

        sender = ""

        if s.find(':') == 0:
            sender, s = s.split(' ', 1)
            sender = sender[1:]

        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()

        command = args.pop(0).upper()

        return sender, command, args

    def __init__(self, state):
        self.state = state
        self.isadmin = False
        self.api = API(self)

    def lineReceived(self, line):
        try:
            sender, command, args = self.parsemsg(line)
        except BadMessage:
            return
        
        if hasattr(self.api, "on_%s" % command.lower()):
            getattr(self.api, "on_%s"% command.lower())(sender, args)

        try:
            self.factory.firehook(command, sender, args)
        except Exception:
            traceback.print_exc(5)

    def sendLine(self, line):
        # Assure that the string isn't unicode.
        return LineReceiver.sendLine(self, str(line))

    def connectionMade(self):
        self.factory.resetDelay()
        self.api.protocol(1)
        self.api.login(self.state["config"]["general"]["nick"],
            self.state["config"]["general"]["password"])
        self.factory.firehook("CONNECTED")

    def connectionLost(self, reason=connectionDone):
        self.factory.firehook("DISCONNECTED", reason)

class ChatFactory(ReconnectingClientFactory, Hookable):
    protocol = Client
    client = None
    
    def __init__(self, state):
        Hookable.__init__(self)
        self.state = state

    def clientConnectionLost(self, connector, unused_reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, unused_reason)
        self.client = None
        self.firehook("CONNECTIONLOST")

    def clientConnectionFailed(self, connector, reason):
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        self.client = None
        self.firehook("CONNECTIONFAILED", reason)

    def buildProtocol(self, addr):
        p = self.protocol(self.state)
        p.factory = self

        self.client = p
        self.firehook("NEWCLIENT", p)
        
        return p

