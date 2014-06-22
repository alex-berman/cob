#!/usr/bin/env python

from sequencer import Sequencer

sequencer = Sequencer()
sequencer.load_sounds("sound/*/*.wav")


# Buses

sequencer.add_bus("bubbles")
sequencer.set_bus_params("bubbles", {
        "reverb_room": 0.5,
        "reverb_mix": 0.6
        })

sequencer.add_bus("long_reverb")
sequencer.set_bus_params("long_reverb", {
        "reverb_room": 0.85,
        "reverb_mix": 0.75
        })

sequencer.add_bus("hannabell_tone_reverb")
sequencer.set_bus_params("long_reverb", {
        "reverb_room": 0.5,
        "reverb_mix": 1.0
        })


# Water

sequencer.set_params(
    "sound/water/Sound 2 mindre rinn.wav",
    {"send": "long_reverb",
     "gain": 7.8})
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


# Mag

sequencer.set_params(
    "sound/mag/mag_weak*.wav",
    {"send": "long_reverb",
     "gain": 2.1,
     "comp_threshold": -36.6})
sequencer.set_params(
    "sound/mag/mag_breath1.wav",
    {"send": "long_reverb",
     "gain": 0,
     "comp_threshold": -36.6})

sequencer.set_params(
    "sound/mag/*.wav",
    {"pan": -1})

sequencer.add_group(
    "sound/mag/*.wav",
    {"silence_min": 10,
     "silence_max": 30})


# Hannabiell

sequencer.set_params(
    "sound/hannabiell/tone*.wav",
    {"send": "hannabell_tone_reverb",
     "gain": -100,
     "comp_threshold": -36.6,
     "send_gain": 12.4})

sequencer.set_params(
    "sound/hannabiell/breath*.wav",
    {"send": "long_reverb",
     "gain": -10.5,
     "comp_threshold": -30.8})

sequencer.set_params(
    "sound/hannabiell/fragment*.wav",
    {"send": "long_reverb",
     "gain": +11.7})

sequencer.set_params(
    "sound/hannabiell/squeak*.wav",
    {"send": "long_reverb",
     "gain": +0.3})


sequencer.set_params(
    "sound/hannabiell/*.wav",
    {"pan": 1})

sequencer.add_group(
    "sound/hannabiell/*.wav",
    {"silence_min": 10,
     "silence_max": 30})


# Run everything

sequencer.run_main_loop()
