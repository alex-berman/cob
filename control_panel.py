#!/usr/bin/env python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from client import WebsocketClient
from event import Event
import re

SLIDER_PRECISION = 1000

PARAMS_CONFIG = {
    "gain":
        {"min": -100,
         "max": 50}
    }

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)

    def _add_controls(self):
        self._layout = QGridLayout()
        self._track_controls = {}
        self._row = 0
        self._add_track_controls()
        self._add_bus_controls()
        self.setLayout(self._layout)

    def _add_track_controls(self):
        for name, track in self._tracks.iteritems():
            self._add_track_control(track)

    def _add_track_control(self, track):
        value = track["params"]["gain"]
        gain_param = PARAMS_CONFIG["gain"]
        gain_slider = self._create_slider()
        gain_slider.valueChanged.connect(
            lambda value: self._slider_value_changed(track["name"], gain_param, value))
        gain_label = QLabel()
        self._add_row([
            QLabel(track["name"]), gain_slider, gain_label])
        self._track_controls[track["name"]] = {"gain_label": gain_label}
        gain_slider.setValue(self._param_value_to_slider_value(gain_param, value))

    def _create_slider(self):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, SLIDER_PRECISION)
        slider.setSingleStep(1)
        slider.setFixedSize(200, 30)
        return slider

    def _param_value_to_slider_value(self, param, value):
        return int(float(value - param["min"]) / (
                param["max"] - param["min"]) * SLIDER_PRECISION)

    def _slider_value_changed(self, track_name, param, slider_value):
        value = self._slider_value_to_param_value(param, slider_value)
        self._track_controls[track_name]["gain_label"].setText(str(value))

    def _slider_value_to_param_value(self, param, slider_value):
        return float(slider_value) / SLIDER_PRECISION * (param["max"] - param["min"]) + \
            param["min"]

    def _add_bus_controls(self):
        for bus in self._buses:
            self._add_bus_control(bus)

    def _add_bus_control(self, bus):
        self._add_row([QLabel(bus)])

    def customEvent(self, custom_qt_event):
        custom_qt_event.callback()

    def received_event(self, event):
        if event.type == Event.CONTROLABLES:
            self._tracks, self._buses = event.content
            self._add_controls()
        else:
            raise Exception("unknown event type %r" % event.type)

    def _add_row(self, cells):
        for column, cell in enumerate(cells):
            self._layout.addWidget(cell, self._row, column, Qt.AlignLeft)
        self._row += 1

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
