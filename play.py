#!/usr/bin/env python

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

sequencer = Sequencer()
time.sleep(1)

sequencer.play_loop(
    "water/Sound 2 mindre rinn.wav",
    gain=7.8)

sequencer.play_loop(
    "water/ZOOM0009a 44100 1.wav",
    gain=-15.6,
    pan=-0.8)
sequencer.play_loop(
    "water/ZOOM0009b 44100 1.wav",
    gain=-15.6,
    pan=0)
sequencer.play_loop(
    "water/ZOOM0009c 44100 1.wav",
    gain=-15.6,
    pan=0.8)

while True:
    time.sleep(1)
