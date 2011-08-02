class NoSuchUser(Exception): pass

class User(object):
    def __init__(self, nick):
        self.nick = nick
        self.isadmin = False
        self.connections = set()

    def sendLine(self, line, exceptions=None):
        if not exceptions:
            exceptions = []

        cnx = self.connections - set(exceptions)

        [ c.sendLine(line) for c in cnx if c.api.welcomed == True ]

    def addConnection(self, cnx):
        if not cnx in self.connections:
            self.connections |= set([cnx,])

    def delConnection(self, cnx):
        if cnx in self.connections:
            try:
                cnx.transport.loseConnection()
            except Exception:
                pass

            self.connections -= set([cnx,])

class UserManager(object):
    def __init__(self, initial=None):
        if initial is None:
            initial = dict()
            
        self.users = initial

    def add(self, nick, cnx):
        try:
            usr = self[nick]
        except NoSuchUser:
            usr = User(nick)
            self.users[nick.lower()] = usr

        usr.addConnection(cnx)

        return usr

    def remove(self, nick):
        usr = self[nick]

        for cnx in usr.connections:
            usr.delConnection(cnx)

        del self.users[nick.lower()]

    def connectionCount(self, nick):
        return len(self[nick].connections)

    def __contains__(self, item):
        item = item.lower()

        if item in self.users:
            return True

        return False

    def __getitem__(self, item):
        item = item.lower()

        if item in self.users:
            return self.users[item]
        
        raise KeyError, item

    def user(self, nick):
        # Wrapper to make sure that the user exists, or
        # throw an exception. Most methods should call
        # this when getting a user.
        nick = nick.lower()

        if nick in self.users:
            return self.users[nick]

        raise NoSuchUser(nick)

    __getitem__ = user
    
    def admins(self):
        return set([user for user in self.users.itervalues() if user.isadmin])

    def all(self):
        return set([user for user in self.users.itervalues()])
