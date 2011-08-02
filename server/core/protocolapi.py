from constants import errorvals
import constants

class API(object):
    protocolid = "1"
    
    def __init__(self, client, state):
        self.protocol = None # What the client reports his protocol is.
        self.welcomed = False
        self.client = client # Connection
        self.state = state
        self.user = None

    def auth(self, command, args):
        if command == "PROTOCOL":
            if not self.protocol:
                if args and args[0] == self.protocolid:
                    self.protocol = args[0]
                    return

                else:
                    # Unsupported protocol identifier
                    self.error(constants.BADPRTCL)
                    self.client.transport.loseConnection()
                    return

        elif self.protocol:
            if command == "LOGIN" and not self.user and args:
                if ":" in args[0]:
                    nick, passwd = args[0].split(":", 1)
                else:
                    self.error(constants.BADLOGIN)
                    return

                if not constants.nickre.match(nick): # ^[-_a-zA-Z0-9]+$
                    # Invalid nick name
                    self.error(constants.INVALIDNICK)
                    return

                configusers = self.state["config"]["users"]

                if nick.lower() in configusers:
                    confpasswd = configusers[nick.lower()]["password"]
                else:
                    self.error(constants.UNKNOWNUSER)
                    return

                if confpasswd and passwd == confpasswd:
                    self.user = self.state["users"].add(nick.lower(), self.client)
                    
                    if configusers[nick.lower()]["isadmin"]:
                        self.user.isadmin = True
                        
                    if not self.welcomed:
                        self.welcome()

                    self.users()
                else:
                    self.error(constants.BADLOGIN)
                    return
            else:
                self.error(constants.NEEDNICK)
                return
        else:
            # You must specify PROTOCOL first
            self.error(constants.NEEDPROTO)

    # Outgoing
    def message(self, nick, message):
        if nick.lower() in self.state["users"]:
            # Someone
            self.directMessage(nick, message, "MESSAGE")

        else:
            if nick == "*":
                # Everyone
                users = self.state["users"].all()
            elif nick == "-":
                # Admins
                users = self.state["users"].admins()
            else:
                self.error(constants.UNKNOWNUSER)
                return
            
            for user in users:
                user.sendLine(":%s MESSAGE %s :%s" %
                    (self.user.nick, nick, message), [self.client,])

    def directMessage(self, nick, message, type):
        nick = nick.lower()
        user = self.state["users"][nick]

        if not self.user.isadmin and not user.isadmin:
            self.error(constants.NOTAUTHD)
            return

        user.sendLine(":%s %s %s :%s" %
            (self.user.nick, type, user.nick, message), [self.client,])

    def users(self):
        # Send list of connected user names to an admin
        line = ",".join([x.nick for x in self.state["users"].admins()])
        self.client.sendLine(":%s ADMINS %s" %
            (self.state["config"]["general"]["servername"],
                line))

        if not self.user.isadmin:
            return

        line = ",".join([x.nick for x in self.state["users"].all()])
        self.client.sendLine(":%s USERS %s" %
            (self.state["config"]["general"]["servername"],
                line))

    def error(self, num):
        if not num in errorvals:
            msg = "Unspecified error"
        else:
            msg = errorvals[num]

        self.client.sendLine(":%s ERROR %i :%s" %
                    (self.state["config"]["general"]["servername"],
                        num, msg))
        
    def welcome(self):
        client = self.client

        client.sendLine(":%s WELCOME %s :%s" %
            (self.state["config"]["general"]["servername"],
                self.user.nick,
                self.state["config"]["general"]["welcome"]))

        self.join()
        
        self.welcomed = True

    def join(self):
        # Only send on the first login (given the possibility of
        # multiple logins.)
        num = len(self.user.connections)
        
        if num == 1:
            if not self.user.isadmin:
                users = self.state["users"].admins()
                
            else:
                users = self.state["users"].all()
                
            for user in users:
                user.sendLine(":%s JOIN %s" %
                (self.state["config"]["general"]["servername"],
                 self.user.nick))

    def leave(self):
        # Only send on the last quit (given the possibility of
        # multiple logins.)
        num = len(self.user.connections)

        if num == 1:
            if self.user.isadmin:
                users = self.state["users"].all()
            else:
                users = self.state["users"].admins()
                
            for user in users:
                user.sendLine(":%s LEAVE %s" %
                    (self.state["config"]["general"]["servername"],
                     self.user.nick))

    def ping(self):
        self.client.sendLine(":%s PING" %
            self.state["config"]["general"]["servername"])
        
    # Incoming
    def on_MESSAGE(self, args):
        if len(args) == 1:
            self.message(None, args[0])
        elif len(args) == 2:
            self.message(args[0], args[1])
