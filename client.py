import ws4py.client.threadedclient
from config import *
import cPickle

class WebsocketClient(ws4py.client.threadedclient.WebSocketClient):
    def __init__(self, host=None):
        if host is None:
            host = "localhost"
        address = "ws://%s:%s%s" % (host, WEBSOCKET_PORT, WEBSOCKET_APPLICATION)
        print address
        ws4py.client.threadedclient.WebSocketClient.__init__(self, address)

    def opened(self):
        print "connected to server"

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, message):
        event = cPickle.loads(str(message))
        print "got from server: %s" % event
        self.received_event(event)

    def received_event(self, event):
        pass

    def send_event(self, event):
        self.send(cPickle.dumps(event))
