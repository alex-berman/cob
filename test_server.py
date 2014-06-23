#!/usr/bin/env python

import time
from client import WebsocketClient

client = WebsocketClient()
client.connect()
client.send("hej hopp")

while True:
    time.sleep(1)
