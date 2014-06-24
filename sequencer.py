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

DEFAULT_SOUND_PARAMS = {
    "pan": 0,
    "gain": 1,
    "fade": None,
    "send": "master",
    "send_gain": 0,
    "comp_threshold": 0}

DEFAULT_BUS_PARAMS = {
    "reverb_mix": 0,
    "reverb_room": 0,
    "reverb_damp": 1}

class Parameters:
    sounds = {}
    buses = {}

class Sequencer:
    def __init__(self):
        self._sounds = {}
        self._tracks = collections.OrderedDict()
        self._buses = []
        self._groups = []
        self._params = Parameters()
        self._scheduler = Scheduler()
        SynthController.kill_potential_engine_from_previous_process()
        self._synth = SynthController()
        self._synth.launch_engine()
        self._synth.connect(self._synth.lang_port)
        self._setup_websocket_server()

    def get_tracks(self):
        return self._tracks

    def get_buses(self):
        return self._buses

    def play(self, sound, looped=0):
        params = self._params.sounds[sound]
        self._synth.play(
            sound,
            params["pan"],
            params["fade"],
            params["gain"],
            looped,
            params["send"],
            params["send_gain"],
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
        self._params.sounds[sound] = copy.copy(DEFAULT_SOUND_PARAMS)

    def add_track(self, name, pattern, params):
        sounds = glob.glob(pattern)
        for sound in sounds:
            self._params.sounds[sound].update(params)
        track = {"name": name,
                 "sounds": sounds}
        self._tracks[name] = track

    def add_group(self, pattern, params):
        group = Group(self, params)
        for sound in glob.glob(pattern):
            group.add(sound)
        self._groups.append(group)

    def add_bus(self, name):
        self._synth.add_bus(name)
        self._buses.append(name)
        self._params.buses[name] = copy.copy(DEFAULT_BUS_PARAMS)

    def set_bus_params(self, bus, new_params):
        params = self._params.buses[bus]
        params.update(new_params)
        self._synth.set_bus_params(
            bus,
            params["reverb_mix"],
            params["reverb_room"],
            params["reverb_damp"])

    def run_main_loop(self):
        while True:
            self._process()
            time.sleep(.1)

    def _process(self):
        self._scheduler.run_scheduled_events()
        for group in self._groups:
            group.process()

    def _setup_websocket_server(self):
        self._server = WebsocketServer(ControlPanelHandler, {"sequencer": self})
        server_thread = threading.Thread(target=self._server.start)
        server_thread.daemon = True
        server_thread.start()


class ControlPanelHandler(ClientHandler):
    def __init__(self, *args, **kwargs):
        self._sequencer = kwargs.pop("sequencer")
        super(ControlPanelHandler, self).__init__(*args, **kwargs)

    def open(self):
        self._send_sounds()

    def _send_sounds(self):
        tracks = self._sequencer.get_tracks()
        buses = self._sequencer.get_buses()
        self.send_event(Event(Event.CONTROLABLES, (tracks, buses)))

    def on_message(self, message):
        print "got message %r" % message


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
