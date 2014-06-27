import config
import liblo
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-r", type=float, default=100.0)
parser.add_argument("-g", type=float, default=100.0)
parser.add_argument("-b", type=float, default=100.0)
args = parser.parse_args()

target = liblo.Address("localhost", config.COLOUR_PORT, liblo.UDP)
liblo.send(target, "/colour", args.r, args.g, args.b)
