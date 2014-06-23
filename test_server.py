#!/usr/bin/env python

import time
from client import WebsocketClient

class Client(WebsocketClient):
    def received_event(self, event):
        print "received event %s" % event

client = WebsocketClient()
client.connect()
client.send("hej hopp")

while True:
    time.sleep(1)
