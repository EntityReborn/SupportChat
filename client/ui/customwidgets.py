from PyQt4 import uic
from PyQt4.QtCore import QEvent, Qt
from PyQt4.QtGui import QMainWindow, QWidget, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout

class MainWindow(QMainWindow):
    def __init__(self, reactor, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.reactor = reactor

    def closeEvent(self, e):
        self.reactor.stop()

class ChatWidget(QWidget):
    def __init__(self, name, id, completer, *args):
        QWidget.__init__(self, *args)
        self.name = name
        self.id = id
        self.completer = completer

    def setupUI(self):
        self.chatbox = cb = QTextEdit(self)
        cb.setReadOnly(True)
        cb.id = self.id

        self.textbox = tb = CompletingLineEdit(self.completer, self)
        tb.id = self.id

        self.sendbutton = sb = QPushButton(self)
        sb.setText("Send")
        sb.id = self.id

        vlayout = QVBoxLayout()
        vlayout.setMargin(0)
        hlayout = QHBoxLayout()
        vlayout.addWidget(cb)
        hlayout.addWidget(tb)
        hlayout.addWidget(sb)
        vlayout.addLayout(hlayout)
        self.setLayout(vlayout)

class CompletionStore(object):
    def __init__(self, initial=None):
        if initial is None:
            initial = []

        self.completions = set(initial)
        self.lastindex = -1

    def addCompletion(self, word):
        if not isinstance(word, list) and \
           not isinstance(word, tuple):
            word = [word,]
        self.completions |= set(word)
        self.reset()

    def delCompletion(self, word):
        if not isinstance(word, list) and \
           not isinstance(word, tuple):
            word = [word,]
        self.completions -= set(word)
        self.reset()

    def setCompletions(self, items):
        self.completions = set(items)
        self.reset()

    def clear(self):
        self.completions = set()
        self.reset()

    def all(self, prefix=None):
        if prefix is None:
            return self.completions

        prefixed = [comp for comp in self.completions \
                if comp.lower().startswith(prefix.lower())]
        
        return prefixed

    def next(self, prefix):
        self.lastindex += 1
        prefixed = self.all(prefix)

        if self.lastindex >= len(prefixed) or self.lastindex == -1:
            self.lastindex = 0

        if prefixed:
            return prefixed[self.lastindex]

        return []

    def reset(self):
        self.lastindex = -1

class CompletingLineEdit(QLineEdit):
    def __init__(self, completer, *args):
        QLineEdit.__init__(self, *args)

        self.completionstore = completer
        self.cursorpos = 0

    def getCurWord(self):
        text = str(self.text())

        if self.cursorpos == -1:
            self.cursorpos = self.cursorPosition()

        wordstart = text.rfind(" ", 0, self.cursorpos) + 1

        pattern = text[wordstart:self.cursorpos]
        return pattern

    def applyCompletion(self, text):
        old = str(self.text())
        wordend = old.find(" ", self.cursorpos)
        wordstart = old.rfind(" ", 0, self.cursorpos) + 1

        if wordend == -1:
            wordend = len(old)

        new = old[:wordstart] + text + old[wordend:]
        self.setText(new)

    def event(self, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                completion = self.completionstore.next(self.getCurWord())

                if not completion:
                    return True
                else:
                    self.applyCompletion(completion)

                return True
            else:
                self.cursorpos = -1
                self.completionstore.reset()

        return QLineEdit.event(self, event)

clientui, x = uic.loadUiType("ui/supporter.ui")
