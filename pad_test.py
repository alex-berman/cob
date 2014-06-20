import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('-sound', type=str,
                    default="water/Sound 2 mindre rinn.wav")
parser.add_argument('-pan', type=float, default=0.)
parser.add_argument('-fade', type=float, default=1.)
args = parser.parse_args()

import liblo
PORT = 57120
target = liblo.Address(PORT)
sound = args.sound
pan = args.pan
liblo.send(target, "/startPad", sound, pan, args.fade)
