#!/usr/bin/env python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from client import WebsocketClient
from event import Event
import threading

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)

    def _add_sound_controls(self):
        self._layout = QVBoxLayout()
        for sound in self._sounds:
            self._add_sound_control(sound)
        self.setLayout(self._layout)

    def _add_sound_control(self, sound):
        self._layout.addWidget(QLabel(sound))

    def customEvent(self, event):
        event.callback()

    def received_event(self, event):
        if event.type == Event.SOUNDS:
            self._sounds = event.content
            self._add_sound_controls()
        else:
            raise Exception("unknown event type %r" % event.type)

class _Event(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, callback):
        QEvent.__init__(self, _Event.EVENT_TYPE)
        self.callback = callback

class Client(WebsocketClient):
    def __init__(self, window):
        self._window = window
        WebsocketClient.__init__(self)

    def received_event(self, event):
        callback = lambda: self._window.received_event(event)
        QApplication.postEvent(self._window, _Event(callback))

app = QApplication(sys.argv)
window = MainWindow()
window.show()
client = Client(window)
client.connect()
app.exec_()
