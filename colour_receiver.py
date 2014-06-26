from osc_receiver import OscReceiver
import liblo

class ColourReceiver(OscReceiver):
    def __init__(self, port=32000):
        OscReceiver.__init__(self, port=port, proto=liblo.UDP)
        self.add_method("/colour", "fff", self._received_colour_message)

    def _received_colour_message(self, path, args, types, src, user_data):
        normalized_rgb = [float(n)/255 for n in args]
        self.received_colour(normalized_rgb)

    def received_colour(self, rgb):
        pass
