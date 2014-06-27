#!/usr/bin/env python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from client import WebsocketClient
from event import Event
import re
import argparse

SLIDER_PRECISION = 1000

PARAMS_CONFIG = {
    "gain_adjustment":
        {"min": -30,
         "max": 30,
         "width": 200},
    "rate":
        {"min": 0.1,
         "max": 3.0,
         "width": 100},

    "max_colour_distance":
        {"min": 0.1,
         "max": 3.0,
         "width": 200},
    }

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self._create_menu()

    def _create_menu(self):
        self._layout = QGridLayout()
        self._menu_bar = QMenuBar()
        self._layout.setMenuBar(self._menu_bar)
        self._create_main_menu()
        self.setLayout(self._layout)

    def _create_main_menu(self):
        self._main_menu = self._menu_bar.addMenu("Main")
        self._add_save_action()
        self._add_restore_action()
        self._add_calibrate_action()

    def _add_save_action(self):
        action = QAction("Save", self)
        action.setShortcut("Ctrl+S")
        action.triggered.connect(
            lambda: client.send_event(Event(Event.SAVE_PARAMS)))
        self._main_menu.addAction(action)

    def _add_restore_action(self):
        action = QAction("Restore", self)
        action.setShortcut("Ctrl+R")
        action.triggered.connect(
            lambda: client.send_event(Event(Event.LOAD_PARAMS)))
        self._main_menu.addAction(action)

    def _add_calibrate_action(self):
        action = QAction("Calibrate", self)
        action.setShortcut("Ctrl+E")
        action.triggered.connect(
            lambda: client.send_event(Event(Event.CALIBRATE_COLOUR)))
        self._main_menu.addAction(action)

    def _add_global_controls(self):
        value = self._params["max_colour_distance"]
        controls = self._create_slider_controls(
            PARAMS_CONFIG["max_colour_distance"],
            value,
            lambda v: self._global_param_value_changed(
                "max_colour_distance", v, manually=True))
        self._global_controls["max_colour_distance"] = controls
        self._add_row([
                QLabel("max colour distance"), controls["slider"], controls["label"]])
            
    def _add_controls(self):
        self._track_controls = {}
        self._global_controls = {}
        self._row = 0
        self._add_global_controls()
        self._add_track_controls()
        self._add_bus_controls()

    def _add_track_controls(self):
        self._add_row([None, QLabel("Gain"), None, QLabel("Pitch")])
        for name, track in self._tracks.iteritems():
            self._add_track_control(track)

    def _add_track_control(self, track):
        row = [QLabel(track["name"])]
        self._track_controls[track["name"]] = {}
        rate_is_controllable = (self._params["tracks"][track["name"]]["age_type"] is None)
        self._add_track_param_control(row, track, "gain_adjustment")
        self._add_track_param_control(row, track, "rate", rate_is_controllable)
        self._add_row(row)

    def _add_track_param_control(self, row, track, param_name, controllable=True):
        value = self._params["tracks"][track["name"]][param_name]
        controls = self._create_slider_controls(
            PARAMS_CONFIG[param_name],
            value,
            lambda v: self._track_param_value_changed(
                track["name"], param_name, v, manually=True),
            controllable)
        self._track_controls[track["name"]][param_name] = controls
        row.append(controls["slider"])
        row.append(controls["label"])

    def _create_slider_controls(self, param, value, on_changed, controllable=True):
        slider = self._create_slider(param["width"])
        slider.setEnabled(controllable)
        slider.sliderMoved.connect(
            lambda v: self._slider_value_changed(on_changed, param, v))
        label = QLabel("%.1f" % value)
        slider.setValue(self._param_value_to_slider_value(param, value))
        return {"slider": slider,
                "label": label}

    def _create_slider(self, width):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, SLIDER_PRECISION)
        slider.setSingleStep(1)
        slider.setFixedSize(width, 30)
        return slider

    def _param_value_to_slider_value(self, param, value):
        return int(float(value - param["min"]) / (
                param["max"] - param["min"]) * SLIDER_PRECISION)

    def _slider_value_changed(self, on_changed, param, slider_value):
        value = self._slider_value_to_param_value(param, slider_value)
        on_changed(value)

    def _track_param_value_changed(self, track_name, param_name, value, manually=False):
        if not manually:
            param = PARAMS_CONFIG[param_name]
            slider_value = self._param_value_to_slider_value(param, value)
            self._track_controls[track_name][param_name]["slider"].setValue(slider_value)
        self._track_controls[track_name][param_name]["label"].setText("%.1f"%value)
        if manually:
            client.send_event(
                Event(Event.SET_TRACK_PARAM,
                      {"track": track_name,
                       "param": param_name,
                       "value": value}))

    def _global_param_value_changed(self, param_name, value, manually=False):
        if not manually:
            param = PARAMS_CONFIG[param_name]
            slider_value = self._param_value_to_slider_value(param, value)
            self._global_controls[param_name]["slider"].setValue(slider_value)
        self._global_controls[param_name]["label"].setText("%.1f"%value)
        if manually:
            client.send_event(
                Event(Event.SET_GLOBAL_PARAM,
                      {"param": param_name,
                       "value": value}))

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
            self._tracks, self._buses, self._params = event.content
            self._add_controls()
        elif event.type == Event.PARAMS:
            self._params = event.content
            self._params_changed()
        else:
            raise Exception("unknown event type %r" % event.type)

    def _params_changed(self):
        self._track_params_changed()
        self._global_params_changed()

    def _track_params_changed(self):
        for track_name in self._tracks.keys():
            for param_name in ["gain_adjustment", "rate"]:
                self._track_param_value_changed(
                    track_name,
                    param_name,
                    self._params["tracks"][track_name][param_name])

    def _global_params_changed(self):
        for param_name in ["max_colour_distance"]:
            self._global_param_value_changed(
                param_name,
                self._params[param_name])

    def _add_row(self, cells):
        for column, cell in enumerate(cells):
            if cell is not None:
                self._layout.addWidget(cell, self._row, column, Qt.AlignLeft)
        self._row += 1

class CustomQtEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, callback):
        QEvent.__init__(self, CustomQtEvent.EVENT_TYPE)
        self.callback = callback

class Client(WebsocketClient):
    def __init__(self, host, window):
        self._window = window
        WebsocketClient.__init__(self, host)

    def received_event(self, event):
        callback = lambda: self._window.received_event(event)
        QApplication.postEvent(self._window, CustomQtEvent(callback))

parser = argparse.ArgumentParser()
parser.add_argument("-host", default="localhost")
args = parser.parse_args()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
client = Client(args.host, window)
client.connect()
app.exec_()
