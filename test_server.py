#!/usr/bin/env python

from client import WebsocketClient
client = WebsocketClient()
client.connect()
client.send("hej hopp")
