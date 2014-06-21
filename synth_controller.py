import liblo
import threading
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
            print "SC: %s" % line
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
            line = self._sc_process.stdout.readline()
            if line:
                print "SC: %s" % line,

    def connect(self, port):
        self._lock = threading.Lock()
        self.target = liblo.Address(port)

    def stop_engine(self):
        if self._sc_listener:
            self._sc_listener.stop()
        if self._sc_process:
            self._sc_process.stdin.write("thisProcess.shutdown;\n")
            self._sc_process.stdin.write("0.exit;\n")
        if self._listening_to_engine:
            self._listening_to_engine = False
            self._send("/shutdown")
            self.logger.info("waiting for SC output thread to finish")
            self._sc_output_thread.join()
            self.logger.info("closing SC pipe")
            self._sc_process.stdin.close()
            self._sc_process.stdout.close()
            self.logger.info("waiting for SC process to exit")
            self._sc_process.wait()
            self.logger.info("SC process exited")
        self.target = None

    def load_sound(self, sound_id, filename):
        self._send("/load", sound_id, filename)
        num_frames_loaded = self._get_load_result(sound_id)
        return num_frames_loaded

    def _get_load_result(self, sound_id, timeout=10.0):
        t = time.time()
        while True:
            if sound_id in self._load_results:
                result = self._load_results[sound_id]
                del self._load_results[sound_id]
                return result
            elif (time.time() - t) > timeout:
                return None
            else:
                self._sc_listener.serve()
                time.sleep(0.01)

    def _handle_loaded(self,path, args, types, src, data):
        sound_id, result = args
        print "got /loaded %s" % args #TEMP
        self._load_results[sound_id] = result

    def play_loop(self, sound, pan=0, fade=0.1, gain=0):
        self._send("/loop", sound, pan, fade, gain)

    def _send(self, command, *args):
        with self._lock:
            liblo.send(self.target, command, *args)
