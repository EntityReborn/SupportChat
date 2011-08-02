class UIAPI(object):
    def __init__(self, ui, state):
        self.ui = ui
        self.state = state
        
    def on_tabindexchanged(self, index):
        widget = self.ui.userPages.widget(index)
        
        if widget:
            self.ui.userPages.setTabText(index, widget.name)

    def on_connected(self):
        self.ui.addChat("Everyone", "*", 0)

    def on_disconnected(self, reason):
        self.ui.addError("Disconnected from server.")
        keys = self.ui.tabdata.keys()
        
        for name in keys:
            self.ui.remChat(name)
            
        self.ui.completer.clear()

    def on_welcome(self, sender, args):
        self.ui.addLog("%s: %s" % (sender, args[1]))

    def on_message(self, sender, args):
        dest, msg = args
        nick = self.state["nick"]
        text = "%s: %s"%(sender, msg)

        if dest == "*":
            self.ui.addChatHistory(text, "*")
        else:
            self.ui.addChatHistory(text, sender)

        if nick.lower() in msg.lower() or dest.lower() == nick.lower():
            self.state["app"].alert(self.state["mainwindow"], 500)
            
        if not dest == "*":
            tabindex = self.ui.tabIndex(sender.lower())
            
            if not tabindex == self.ui.userPages.currentIndex():
                tabtext = self.ui.tabdata[sender.lower()].name
                newtext = "*%s*"%tabtext
                self.ui.userPages.setTabText(tabindex, newtext)
            
    def on_admins(self, sender, args):
        self.ui.userPages.tabBar().show()

        admins = set(args[0].split(","))
        
        for user in admins:
            if not user.lower() in self.ui.tabdata:
                self.ui.addChat(user)

    def on_users(self, sender, args):
        self.ui.userPages.tabBar().show()

        users = set(args[0].split(","))
        
        for user in users:
            if not user.lower() in self.ui.tabdata:
                self.ui.addChat(user)

    def on_join(self, sender, args):
        self.ui.addChat(args[0])
        self.ui.addLog("* %s joined." % args[0])

    def on_leave(self, sender, args):
        self.ui.remChat(args[0])
        self.ui.addLog("* %s left." % args[0])
