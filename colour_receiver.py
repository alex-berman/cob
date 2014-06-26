from osc_receiver import OscReceiver
import liblo

class ColourReceiver(OscReceiver):
    def __init__(self):
        OscReceiver.__init__(self, port=32000, proto=liblo.UDP)
        self.add_method("/colour", "fff", self._received_colour)

    def _received_colour(self, path, args, types, src, user_data):
        print path, args, types, src, user_data

