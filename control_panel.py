#!/usr/bin/env python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from client import WebsocketClient
from event import Event
import re

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)

    def _add_sound_controls(self):
        self._layout = QVBoxLayout()
        for sound in sorted(self._sounds):
            self._add_sound_control(sound)
        self.setLayout(self._layout)

    def _add_sound_control(self, sound):
        self._layout.addWidget(QLabel(self._sound_label(sound)))

    def _sound_label(self, filename):
        matcher = re.match(r"sound\/(.*)\.wav", filename)
        if matcher:
            return matcher.group(1)
        else:
            return filename

    def customEvent(self, custom_qt_event):
        custom_qt_event.callback()

    def received_event(self, event):
        if event.type == Event.SOUNDS:
            self._sounds = event.content
            self._add_sound_controls()
        else:
            raise Exception("unknown event type %r" % event.type)

class CustomQtEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, callback):
        QEvent.__init__(self, CustomQtEvent.EVENT_TYPE)
        self.callback = callback

class Client(WebsocketClient):
    def __init__(self, window):
        self._window = window
        WebsocketClient.__init__(self)

    def received_event(self, event):
        callback = lambda: self._window.received_event(event)
        QApplication.postEvent(self._window, CustomQtEvent(callback))

app = QApplication(sys.argv)
window = MainWindow()
window.show()
client = Client(window)
client.connect()
app.exec_()
