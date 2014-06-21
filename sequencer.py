from synth_controller import SynthController
import time

class Sequencer:
    def __init__(self):
        SynthController.kill_potential_engine_from_previous_process()
        self._synth = SynthController()
        self._synth.launch_engine()
        self._synth.connect(self._synth.lang_port)

    def play_loop(self, *args, **kwargs):
        self._synth.play_loop(*args, **kwargs)

    def run_main_loop(self):
        while True:
            time.sleep(1)
