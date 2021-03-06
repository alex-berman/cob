import liblo
import threading
from osc_receiver import OscReceiver
import time
import subprocess
import re
import logging

class SynthController:
    @staticmethod
    def kill_potential_engine_from_previous_process():
        subprocess.call("killall --quiet sclang", shell=True)
        subprocess.call("killall --quiet scsynth", shell=True)

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger("SynthController")
        self.logger = logger
        self._sc_process = None
        self._sc_listener = None
        self._listening_to_engine = False

    def launch_engine(self):
        self.stop_engine()

        self._sc_process = subprocess.Popen("sclang sc/engine.sc", shell=True,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE)
        self._listening_to_engine = True
        self.lang_port = None
        initialized = False
        while self.lang_port is None or not initialized:
            line = self._sc_process.stdout.readline().strip()
            self._log("SC: %s" % line)
            m = re.search('langPort=(\d+)', line)
            if m:
                self.lang_port = int(m.group(1))
            elif line == "Receiving notification messages from server localhost":
                initialized = True
        self._sc_output_thread = threading.Thread(name="SynthController._sc_output_thread",
                                                  target=self._read_sc_output)
        self._sc_output_thread.daemon = True
        self._sc_output_thread.start()
        self._await_synths_to_be_loaded()

    def _await_synths_to_be_loaded(self):
        time.sleep(1)

    def _read_sc_output(self):
        while self._listening_to_engine:
            line = self._sc_process.stdout.readline().strip("\r\n")
            if line:
                self._log("SC: %s" % line)

    def connect(self, port):
        self._lock = threading.Lock()
        self.target = liblo.Address(port)
        self._subscribe_to_info()

    def _subscribe_to_info(self):
        self._sounds_info = {}
        if not self._sc_listener:
            self._sc_listener = OscReceiver(proto=liblo.TCP, name="SynthController")
            self._sc_listener.add_method(
                "/loaded", "sii", self._handle_loaded)
            self._sc_listener.add_method(
                "/stopped_playing", "s", self._handle_stopped_playing)
            self._sc_listener.start()
        self._send("/info_subscribe", self._sc_listener.port)

    def stop_engine(self):
        if self._sc_listener:
            self._sc_listener.stop()
        if self._sc_process:
            self._sc_process.stdin.write("thisProcess.shutdown;\n")
            self._sc_process.stdin.write("0.exit;\n")
        if self._listening_to_engine:
            self._listening_to_engine = False
            self._send("/shutdown")
            self._log("waiting for SC output thread to finish")
            self._sc_output_thread.join()
            self._log("closing SC pipe")
            self._sc_process.stdin.close()
            self._sc_process.stdout.close()
            self._log("waiting for SC process to exit")
            self._sc_process.wait()
            self._log("SC process exited")
        self.target = None

    def load_sound(self, filename):
        self._send("/load", filename)
        num_frames_loaded = self._get_load_result(filename)
        return num_frames_loaded

    def _get_load_result(self, filename, timeout=10.0):
        t = time.time()
        while True:
            if filename in self._sounds_info:
                result = self._sounds_info[filename]
                return result
            elif (time.time() - t) > timeout:
                return None
            else:
                self._sc_listener.serve()
                time.sleep(0.01)

    def _handle_loaded(self, path, args, types, src, data):
        filename, num_frames, sample_rate = args
        print "got /loaded %s" % args
        duration = float(num_frames) / sample_rate
        print "duration=%s" % duration
        self._sounds_info[filename] = {
            "duration": duration,
            "is_playing": False
            }

    def _handle_stopped_playing(self, path, args, types, src, data):
        sound = args[0]
        self._sounds_info[sound]["is_playing"] = False
        print "stopped playing %s" % sound

    def play(self, sound, pan, fade, gain, rate, looped, send, send_gain, comp_threshold):
        if fade is None:
            if looped:
                fade = .1
            else:
                fade = 0

        self._send(
            "/play", sound, pan, fade, gain, rate, looped, send, send_gain, comp_threshold)
        self._sounds_info[sound]["is_playing"] = True

    def get_duration(self, sound):
        return self._sounds_info[sound]["duration"]

    def is_playing(self, sound):
        return self._sounds_info[sound]["is_playing"]

    def add_bus(self, name):
        self._send("/add_bus", name)

    def set_bus_params(self, name, mix, room, damp):
        self._send("/set_bus_params", name, mix, room, damp)

    def _send(self, command, *args):
        with self._lock:
            liblo.send(self.target, command, *args)

    def _log(self, string):
        print string
        self.logger.debug(string)

    def set_param(self, sound, param, value):
        self._send("/set_%s" % param, sound, value)

    def process(self):
        self._sc_listener.serve()
