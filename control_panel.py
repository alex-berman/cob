#!/usr/bin/env python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from client import WebsocketClient
from event import Event
import re

SLIDER_PRECISION = 1000

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)

    def _add_controls(self):
        self._layout = QFormLayout()
        self._add_sound_controls()
        self._add_bus_controls()
        self.setLayout(self._layout)

    def _add_sound_controls(self):
        for sound in sorted(self._sounds):
            self._add_sound_control(sound)

    def _add_sound_control(self, sound):
        gain_slider = self._create_slider()
        self._layout.addRow(
            QLabel(self._sound_label(sound)),
            gain_slider)

    def _create_slider(self):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, SLIDER_PRECISION)
        slider.setSingleStep(1)
        slider.setFixedSize(100, 20)
        return slider
    
    def _add_bus_controls(self):
        for bus in self._buses:
            self._add_bus_control(bus)

    def _add_bus_control(self, bus):
        self._layout.addRow(QLabel(bus))

    def _sound_label(self, filename):
        matcher = re.match(r"sound\/(.*)\.wav", filename)
        if matcher:
            return matcher.group(1)
        else:
            return filename

    def customEvent(self, custom_qt_event):
        custom_qt_event.callback()

    def received_event(self, event):
        if event.type == Event.CONTROLABLES:
            self._sounds, self._buses = event.content
            self._add_controls()
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
