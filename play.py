#!/usr/bin/env python

from sequencer import Sequencer
import glob

sequencer = Sequencer()

for sound in glob.glob("sound/*/*.wav"):
    sequencer.load_sound(sound)

sequencer.play_loop(
    "sound/water/Sound 2 mindre rinn.wav",
    gain=7.8)

sequencer.play_loop(
    "sound/water/ZOOM0009a 44100 1.wav",
    gain=-15.6,
    pan=-0.8)
sequencer.play_loop(
    "sound/water/ZOOM0009b 44100 1.wav",
    gain=-15.6,
    pan=0)
sequencer.play_loop(
    "sound/water/ZOOM0009c 44100 1.wav",
    gain=-15.6,
    pan=0.8)

sequencer.run_main_loop()
