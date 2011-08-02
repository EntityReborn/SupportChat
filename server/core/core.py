from collections import defaultdict
import traceback

from twisted.protocols import basic
from twisted.internet import protocol, reactor

import constants
from protocolapi import API
from hooks import Hookable
from users import UserManager

class BadMessage(Exception): pass

class ConnectingClient(basic.LineReceiver):
    def __init__(self, state):
        self.api = API(self, state)
        self.state = state

    def parsemsg(self, s):
        if not s:
            raise BadMessage

        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()

        command = args.pop(0).upper()

        return command, args

    _ping_deferred = None

    def _idle_ping(self):
        self._ping_deferred = None
        self._reconnect_deferred = reactor.callLater(
            self.factory.pong_timeout, self._timeout_reconnect)

        self.api.ping()

    def _timeout_reconnect(self):
        self.factory.firehook("TIMEDOUT", self)
        self.transport.loseConnection()

    def on_pong(self, args):
        if self._reconnect_deferred:
            self._reconnect_deferred.cancel()
            self._reconnect_deferred = None
            
            self._ping_deferred = reactor.callLater(
                self.factory.ping_interval, self._idle_ping)
    
    def connectionMade(self):
        self.factory.firehook("CONNECTED", self)
        #self._ping_deferred = reactor.callLater(self.factory.ping_interval, self._idle_ping)

    def connectionLost(self, reason):
        self.factory.firehook("DISCONNECTED", self, reason)

        if self.api.welcomed:
            self.api.leave()

            self.state["users"][self.api.user.nick].delConnection(self)
            
    def lineReceived(self, line):
        if self._ping_deferred is not None:
            self._ping_deferred.reset(self.factory.ping_interval)
            
        try:
            command, args = self.parsemsg(line)
        except BadMessage:
            self.api.error(constants.BADMSG) # Bad or empty message
            return
        try:
            if self.api.welcomed:
                self.parseMessage(command, args)
            else:
                self.api.auth(command, args)
        except Exception:
            traceback.print_exc(5)

    def parseMessage(self, command, args):
        handled = False

        self.factory.firehook("MESSAGE", self, command, args)

        for thing in [self, self.api]:
            if hasattr(thing, "on_%s"%command):
                try:
                    handled = True
                    getattr(thing, "on_%s"%command)(args)
                except Exception, e:
                    traceback.print_exc(5)
                    
        if not handled:
            self.api.error(constants.BADMSG)

    def sendLine(self, line):
        if self._ping_deferred is not None:
            self._ping_deferred.reset(self.factory.ping_interval)

        self.factory.firehook("SENDLINE", self, line)
        basic.LineReceiver.sendLine(self, line)

class ChatFactory(protocol.ServerFactory, Hookable):
    protocol = ConnectingClient

    ping_interval = 60.0
    pong_timeout = 240.0
    
    def __init__(self, state):
        Hookable.__init__(self)

        if not "users" in state:
            state["users"] = UserManager()

        self.state = state

    def buildProtocol(self, addr):
        p = self.protocol(self.state)
        p.factory = self
        return p
