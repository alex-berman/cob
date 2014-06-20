import argparse
import time
from simple_osc_sender import OscSender

parser = argparse.ArgumentParser()
parser.add_argument('-sound', type=str,
                    default="water/Sound 2 mindre rinn.wav")
parser.add_argument('-pan', type=float, default=0.)
parser.add_argument('-fade', type=float, default=1.)
parser.add_argument("-gain", type=float, default=0.)
args = parser.parse_args()

PORT = 57120
target = OscSender(PORT)
sound = args.sound
pan = args.pan
target.send("/loop", sound, pan, args.fade, args.gain)
