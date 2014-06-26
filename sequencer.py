from synth_controller import SynthController
import time
import glob
import random
from scheduler import Scheduler
import copy
from server import WebsocketServer, ClientHandler
import threading
from event import Event
import collections
import logging
import cPickle
import os
from colour_receiver import ColourReceiver

PARAMS_FILENAME = "params.data"

DEFAULT_SOUND_PARAMS = {
    "pan": 0,
    "gain": 0,
    "fade": None,
    "send": "master",
    "send_gain": 0,
    "gain_adjustment": 0,
    "comp_threshold": 0,
    "rate": 1}

DEFAULT_BUS_PARAMS = {
    "reverb_mix": 0,
    "reverb_room": 0,
    "reverb_damp": 1}

class Sequencer:
    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger("Sequencer")
        self.logger = logger
        self._params = {"tracks": {},
                        "buses": {},
                        "reference_colour": None}
        self._sounds = {}
        self._tracks = collections.OrderedDict()
        self._buses = collections.OrderedDict()
        self._groups = []
        self._scheduler = Scheduler()
        self._setup_colour_receiver()
        SynthController.kill_potential_engine_from_previous_process()
        self._synth = SynthController()
        self._synth.launch_engine()
        self._synth.connect(self._synth.lang_port)
        self._setup_websocket_server()

    def _setup_colour_receiver(self):
        self._current_colour = None
        self._colour_receiver = ColourReceiver()
        self._colour_receiver.received_colour = self.set_current_colour        
        self._colour_receiver.start()

    def set_current_colour(self, rgb):
        self._current_colour = rgb

    def calibrate_colour(self):
        self.log("calibrate_colour %s" % self._current_colour)
        if self._current_colour is not None:
            self._params["reference_colour"] = self._current_colour

    def get_tracks(self):
        return self._tracks

    def get_buses(self):
        return self._buses

    def get_params(self):
        return self._params

    def play(self, sound, looped=0):
        track_name = self._sounds[sound]["track_name"]
        track = self._tracks[track_name]
        params = self._params["tracks"][track_name]
        self._synth.play(
            sound,
            params["pan"],
            params["fade"],
            params["gain"] + params["gain_adjustment"],
            params["rate"],
            looped,
            params["send"],
            params["send_gain"] + params["gain_adjustment"],
            params["comp_threshold"])
        self._sounds[sound]["is_playing"] = True
        if looped == 0:
            self.schedule(
                action=lambda: self._stopped_playing(sound),
                delay=self._synth.get_duration(sound))

    def schedule(self, action, delay):
        self._scheduler.schedule(action, delay)

    def is_playing(self, sound):
        return self._sounds[sound]["is_playing"]

    def _stopped_playing(self, sound):
        self._sounds[sound]["is_playing"] = False

    def load_sounds(self, pattern):
        for sound in glob.glob(pattern):
            self.load_sound(sound)

    def load_sound(self, sound):
        self._synth.load_sound(sound)
        self._sounds[sound] = {"is_playing": False}

    def add_track(self, name, pattern, params_overrides):
        params = copy.copy(DEFAULT_SOUND_PARAMS)
        params.update(params_overrides)
        sounds = glob.glob(pattern)
        track = {"name": name,
                 "sounds": sounds}
        self._params["tracks"][name] = params
        for sound in sounds:
            self._sounds[sound]["track_name"] = name
        self._tracks[name] = track

    def add_group(self, pattern, params):
        group = Group(self, params)
        for sound in glob.glob(pattern):
            group.add(sound)
        self._groups.append(group)

    def add_bus(self, name):
        self._synth.add_bus(name)
        self._buses[name] = {"name": name}
        self._params["buses"][name] = DEFAULT_BUS_PARAMS

    def set_bus_params(self, bus, new_params):
        params = self._params["buses"][bus]
        params.update(new_params)
        self._synth.set_bus_params(
            bus,
            params["reverb_mix"],
            params["reverb_room"],
            params["reverb_damp"])

    def try_to_load_params(self):
        if os.path.exists(PARAMS_FILENAME):
            self.load_params()

    def run_main_loop(self):
        while True:
            self._process()
            time.sleep(.1)

    def _process(self):
        self._scheduler.run_scheduled_events()
        self._colour_receiver.serve()
        for group in self._groups:
            group.process()

    def _setup_websocket_server(self):
        self._server = WebsocketServer(ControlPanelHandler, {"sequencer": self})
        server_thread = threading.Thread(target=self._server.start)
        server_thread.daemon = True
        server_thread.start()

    def set_param(self, track_name, param, value):
        track = self._tracks[track_name]
        params = self._params["tracks"][track_name]
        params[param] = value
        self._on_track_params_changed(track)

    def _on_tracks_params_changed(self):
        for track in self._tracks.values():
            self._on_track_params_changed(track)

    def _on_track_params_changed(self, track):
        params = self._params["tracks"][track["name"]]
        for sound in track["sounds"]:
            if self._sounds[sound]["is_playing"]:
                self._synth.set_param(sound, "gain",
                                      params["gain"] + params["gain_adjustment"])
                self._synth.set_param(sound, "send_gain",
                                      params["send_gain"] + params["gain_adjustment"])
                self._synth.set_param(sound, "rate", params["rate"])

    def save_params(self):
        f = open(PARAMS_FILENAME, "w")
        cPickle.dump(self._params, f)
        f.close()

    def load_params(self):
        f = open(PARAMS_FILENAME, "r")
        self._params = cPickle.load(f)
        self._on_tracks_params_changed()
        f.close()
        
    def log(self, string):
        print string
        self.logger.debug(string)


class ControlPanelHandler(ClientHandler):
    def __init__(self, *args, **kwargs):
        self._sequencer = kwargs.pop("sequencer")
        super(ControlPanelHandler, self).__init__(*args, **kwargs)

    def open(self):
        self._send_sounds()

    def _send_sounds(self):
        tracks = self._sequencer.get_tracks()
        buses = self._sequencer.get_buses()
        params = self._sequencer.get_params()
        self.send_event(Event(Event.CONTROLABLES, (tracks, buses, params)))

    def received_event(self, event):
        if event.type == Event.SET_PARAM:
            self._sequencer.set_param(
                event.content["track"],
                event.content["param"],
                event.content["value"])
        elif event.type == Event.SAVE_PARAMS:
            self._sequencer.save_params()
        elif event.type == Event.LOAD_PARAMS:
            self._sequencer.load_params()
            self.send_event(Event(Event.PARAMS, self._sequencer.get_params()))
        elif event.type == Event.CALIBRATE_COLOUR:
            self._sequencer.calibrate_colour()
        else:
            self._sequencer.log("WARNING: unknown event type %r" % event.type)


PLAYING, IDLE, WAITING_TO_PLAY = range(3)

class Group:
    def __init__(self, sequencer, params):
        self._sequencer = sequencer
        self._params = params
        self._sounds = []
        self._state = IDLE

    def add(self, sound):
        self._sounds.append(sound)

    def process(self):
        if self._state == IDLE:
            self._schedule_play()
            self._finished_waiting = False
            self._state = WAITING_TO_PLAY

        elif self._state == PLAYING:
            if not self._sequencer.is_playing(self._active_sound):
                self._state = IDLE

        elif self._state == WAITING_TO_PLAY:
            if self._finished_waiting:
                self._play_something()
                self._state = PLAYING

    def _schedule_play(self):
        silence_duration = random.uniform(
            self._params["silence_min"],
            self._params["silence_max"])
        self._sequencer.schedule(
            lambda: self.finished_waiting(),
            silence_duration)

    def finished_waiting(self):
        self._finished_waiting = True

    def _play_something(self):
        self._active_sound = random.choice(self._sounds)
        self._sequencer.play(self._active_sound)
