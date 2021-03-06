#!/usr/bin/env python

STEREO_WIDTH = .2

MAG_PAN = -1 * STEREO_WIDTH
HANNABIELL_PAN = 1 * STEREO_WIDTH

MAG_AGE_TYPE = "decay"
HANNABIELL_AGE_TYPE = "rejuvinate"

from sequencer import Sequencer
import logging

logging.basicConfig(filename="play.log",
                    level=logging.DEBUG,
                    filemode="w",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

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

sequencer.add_track(
    "rumbling water",
    "sound/water/Sound 2 mindre rinn.wav",
    {"send": "long_reverb",
     "gain": 7.8,
     "rate": 1.0,
     })
sequencer.add_track(
    "bubbles1",
    "sound/water/ZOOM0009a 44100 1.wav",
    {"send": "bubbles",
     "gain": -35.6,
     "rate": 0.5,
     "pan": -0.8})
sequencer.add_track(
    "bubbles2",
    "sound/water/ZOOM0009b 44100 1.wav",
    {"send": "bubbles",
     "gain": -35.6,
     "rate": 0.5,
     "gain_adjustment": -20,
     "pan": 0})
sequencer.add_track(
    "bubbles3",
    "sound/water/ZOOM0009c 44100 1.wav",
    {"send": "bubbles",
     "gain": -35.6,
     "rate": 0.5,
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

sequencer.add_track(
    "mag weak",
    "sound/mag/mag_weak*.wav",
    {"send": "long_reverb",
     "gain": 2.1,
     "comp_threshold": -36.6,
     "age_type": MAG_AGE_TYPE,
     "pan": MAG_PAN})
sequencer.add_track(
    "mag breath",
    "sound/mag/mag_breath1.wav",
    {"send": "long_reverb",
     "gain": 0,
     "comp_threshold": -36.6,
     "age_type": MAG_AGE_TYPE,
     "pan": MAG_PAN})

sequencer.add_group(
    "sound/mag/*.wav",
    {"silence_min": 15,
     "silence_max": 40})


# Hannabiell

sequencer.add_track(
    "hannabiell tone",
    "sound/hannabiell/tone*.wav",
    {"send": "hannabell_tone_reverb",
     "gain": -100,
     "comp_threshold": -36.6,
     "send_gain": 12.4,
     "age_type": HANNABIELL_AGE_TYPE,
     "pan": HANNABIELL_PAN})

sequencer.add_track(
    "hannabiell breath",
    "sound/hannabiell/breath*.wav",
    {"send": "long_reverb",
     "gain": -10.5,
     "comp_threshold": -30.8,
     "age_type": HANNABIELL_AGE_TYPE,
     "pan": HANNABIELL_PAN})

sequencer.add_track(
    "hannabiell fragment",
    "sound/hannabiell/fragment*.wav",
    {"send": "long_reverb",
     "gain": +11.7,
     "age_type": HANNABIELL_AGE_TYPE,
     "pan": HANNABIELL_PAN})

sequencer.add_track(
    "hannabiell squeak",
    "sound/hannabiell/squeak*.wav",
    {"send": "long_reverb",
     "gain": +0.3,
     "age_type": HANNABIELL_AGE_TYPE,
     "pan": HANNABIELL_PAN})


sequencer.add_group(
    "sound/hannabiell/*.wav",
    {"silence_min": 15,
     "silence_max": 40})


# Run everything

sequencer.try_to_load_params()
sequencer.run_main_loop()
