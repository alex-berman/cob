#!/usr/bin/env python

from sequencer import Sequencer

sequencer = Sequencer()
sequencer.add_bus("bubbles")
sequencer.set_bus_params("bubbles", {
        "reverb_room": 0.5,
        "reverb_mix": 0.6
        })

sequencer.load_sounds("sound/*/*.wav")
sequencer.set_params(
    "sound/water/Sound 2 mindre rinn.wav",
    {"gain": 7.8})
sequencer.set_params(
    "sound/water/ZOOM0009a 44100 1.wav",
    {"send": "bubbles",
     "gain": -15.6,
     "pan": -0.8})
sequencer.set_params(
    "sound/water/ZOOM0009b 44100 1.wav",
    {"send": "bubbles",
     "gain": -15.6,
     "pan": 0})
sequencer.set_params(
    "sound/water/ZOOM0009c 44100 1.wav",
    {"send": "bubbles",
     "gain": -15.6,
     "pan": 0.8})

sequencer.play(
    "sound/water/Sound 2 mindre rinn.wav",
    looped=1)
sequencer.play(
    "sound/water/ZOOM0009a 44100 1.wav",
    looped=1)
sequencer.play(
    "sound/water/ZOOM0009b 44100 1.wav",
    looped=1)
sequencer.play(
    "sound/water/ZOOM0009c 44100 1.wav",
    looped=1)

sequencer.add_group(
    "sound/mag/mag_weak*.wav",
    {"pan": -1})
sequencer.add_group(
    "sound/hannabiell/tone*.wav",
    {"pan": 1})

sequencer.run_main_loop()
