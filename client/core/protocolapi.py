class API(object):
    def __init__(self, client):
        self.client = client
        
    # Incoming
    def on_welcome(self, sender, args):
        nick, message = args
        self.client.state["nick"] = self.client.nick = nick

    def on_users(self, sender, args):
        self.client.isadmin = True

    def on_ping(self, sender, args):
        self.pong()

    # Outgoing
    def ping(self):
        self.client.sendLine("PING")

    def pong(self):
        self.client.sendLine("PONG")
        
    def protocol(self, id):
        self.client.sendLine("PROTOCOL %i" % id)

    def login(self, nick, passwd):
        self.client.sendLine("LOGIN %s:%s" % (nick, passwd))

    def message(self, line, to=None):
        if not to or not self.client.isadmin:
            to = ""

        if not line:
            return

        self.client.sendLine("MESSAGE %s :%s" % (to, line))

    def action(self, line, to=None):
        if not to or not self.client.isadmin:
            to = ""

        if not line:
            return

        self.client.sendLine("ACTION %s :%s" % (to, line))
