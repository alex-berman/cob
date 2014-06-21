#!/usr/bin/env python

from sequencer import Sequencer

sequencer = Sequencer()
sequencer.load_sounds("sound/*/*.wav")

sequencer.play(
    "sound/water/Sound 2 mindre rinn.wav",
    looped=1,
    gain=7.8)

sequencer.play(
    "sound/water/ZOOM0009a 44100 1.wav",
    looped=1,
    gain=-15.6,
    pan=-0.8)
sequencer.play(
    "sound/water/ZOOM0009b 44100 1.wav",
    looped=1,
    gain=-15.6,
    pan=0)
sequencer.play(
    "sound/water/ZOOM0009c 44100 1.wav",
    looped=1,
    gain=-15.6,
    pan=0.8)

#sequencer.add_group("sound/mag/mag_weak*.wav")
sequencer.add_group("sound/hannabiell/tone*.wav")

sequencer.run_main_loop()
