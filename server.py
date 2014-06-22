from config import *
import tornado.web
import tornado.ioloop
import tornado.websocket
from tornado.httpserver import HTTPServer

class ClientHandler(tornado.websocket.WebSocketHandler):
    def on_message(self, message):
        print "got message %r" % message

class WebsocketServer(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(
            self,
            [(WEBSOCKET_APPLICATION, ClientHandler)],
            debug=True)
        self._loop = tornado.ioloop.IOLoop.instance()
        self._listen(WEBSOCKET_PORT)

    def _listen(self, port, address="", **kwargs):
        self._server = HTTPServer(self, **kwargs)
        self._server.listen(port, address)

    def start(self):
        self._loop.start()

    def stop(self):
        self._loop.stop()
        self._server.stop()
