from datetime import datetime

from PyQt4.QtCore import QObject

from uiapi import UIAPI
from customwidgets import clientui, ChatWidget, CompletionStore

class Ui(clientui, QObject):
    def __init__(self, state, *args):
        clientui.__init__(self, *args)
        QObject.__init__(self, *args)
        
        self.tabdata = {}   # {tabname: ChatWidget(), ...}

        self.uiapi = UIAPI(self, state)
        self.state = state
        self.completer = CompletionStore()
        
    def setupUi(self, *args):
        clientui.setupUi(self, *args)
        self.userPages.currentChanged.connect(self.uiapi.on_tabindexchanged)
        
    def hook(self, command, *args):
        for thing in [self, self.uiapi]:
            if hasattr(thing, "on_%s"%command.lower()):
                getattr(thing, "on_%s"%command.lower())(*args)

    def timestamp(self):
        ampm = "AM"
        t = datetime.now()
        h = t.hour % 12

        if t.hour > h:
            ampm = "PM"

        m = t.minute
        s = t.second
        
        return "{0}:{1:02}:{2:02}{3}".format(h, m, s, ampm)

    def addChat(self, name, key=None, index=None):
        if not key:
            key = str(name).lower()
        else:
            key = str(key).lower()

        if not key in self.tabdata:
            widget = ChatWidget(name, key,
                                self.completer, self.userPages)
            
            if index is None:
                index = self.userPages.addTab(widget, name)
            else:
                self.userPages.insertTab(index, widget, name)

            widget.setupUI()

            widget.textbox.returnPressed.connect(self.sendChat)
            widget.sendbutton.clicked.connect(self.sendChat)
            
            self.tabdata[key] = widget
            self.completer.addCompletion(str(name))

    def remChat(self, key):
        lkey = str(key).lower()

        if not lkey in self.tabdata:
            return
        else:
            index = self.userPages.indexOf(self.tabdata[lkey])
            self.userPages.removeTab(index)
            del self.tabdata[lkey]

        self.completer.delCompletion(str(key))

    def chatBox(self, name=None):
        if not self.state["factory"].client:
            return self.logText

        if name is None:
            index = self.userPages.currentIndex()
            name = str(self.userPages.tabText(index))
        else:
            name = str(name)
        
        return self.tabdata[name.lower()].chatbox

    def textBox(self, name=None):
        if name is None:
            index = self.userPages.currentIndex()
            name = str(self.userPages.tabText(index))
        else:
            name = str(name)
        
        return self.tabdata[name.lower()].textbox
        
    def tabIndex(self, name=None):
        if name is None:
            index = self.userPages.currentIndex()
            return index
        else:
            name = str(name)
            widget = self.tabdata[name.lower()]
            index = self.userPages.indexOf(widget)
            return index
    
    def addChatHistory(self, line, name):
        name = name.lower()
        self.chatBox(name).append("[%s] %s" % (self.timestamp(), line))

    def addError(self, line):
        self.addLog("ERROR: %s" % line)

    def addLog(self, line):
        self.logText.append("[%s] %s" % (self.timestamp(), line))

    def sendChat(self):
        indexname = self.sender().id.lower()
        
        client = self.state["factory"].client

        if client:
            tabdata = self.tabdata[indexname]

            if indexname != "log":
                text = str(tabdata.textbox.text())

                self.addChatHistory("%s: %s" % (client.nick, text), indexname)

                if indexname != "everyone" and client.isadmin:
                    client.api.message(text, indexname)
                else:
                    client.api.message(text)

            tabdata.textbox.clear()
        else:
            self.addError("You are currently not connected to the server.")
            
    def disconnected(self):
        keys = self.tabdata.keys()
        
        for name in keys:
            self.remChat(name)
            
        self.completer.clear()
