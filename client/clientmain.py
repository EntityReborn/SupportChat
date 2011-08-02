from core.qt4reactor import install
install()

from PyQt4 import QtGui

import sys
app = QtGui.QApplication(sys.argv)

from twisted.internet import reactor

from core.chatclient import ChatFactory
from core.config import loadConfig

from ui.clientui import Ui
from ui.customwidgets import MainWindow

class Main(object):
    def __init__(self, state):
        self.state = state
        self.main = MainWindow(reactor)
        self.dialog = Ui(self.state)

        self.dialog.setupUi(self.main)
        
        self.state["dialog"] = self.dialog
        self.state["mainwindow"] = self.main

    def run(self):
        self.main.show()
        f = ChatFactory(self.state)
        self.state["factory"] = f
        f.addhook("*", self.state["dialog"].hook)
        self.state["dialog"].addLog("Connecting to the server...")
        general = self.state["config"]["general"]
        reactor.connectTCP(general["server"], int(general["port"]), f)
        reactor.run()

if __name__ == '__main__':
    config = loadConfig("client.conf", "conf")
    if not config:
        exit(1)
        
    state = {
        "reactor": reactor,
        "app": app,
        "config": config,
    }

    m = Main(state)
    m.run()
