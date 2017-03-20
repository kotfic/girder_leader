import girder
import zmq
import cherrypy
import threading
from zmq.eventloop import ioloop, zmqstream


class ZMQThread(threading.Thread):
    def __init__(self, bus):
        threading.Thread.__init__(self)
        self.bus = bus
        self.daemon = True
        self.terminate = False

    def process_message(self, stream, messages):
        for msg in messages:
            if msg == 'Exit':
                stream.send("Bye!")
                ioloop.IOLoop.instance().stop()
                break
            else:
                stream.send("Recieved: \"{}\"".format(msg))
                self.bus.publish('zmq_message', msg)

# IO loop polling
# Note that ioloop.DelayedCallback looks like it can be used for
# leader election timers etc - or maybe ioloop.PeriodicCallback?
    def run(self):
        girder.logprint.info("Starting 0MQ Thread")
        self.context = zmq.Context()
        socket = self.context.socket(zmq.REP)
        socket.bind('tcp://*:5555')

        stream = zmqstream.ZMQStream(socket)
        stream.on_recv_stream(self.process_message)

        ioloop.IOLoop.instance().start()


    def stop(self):
        """
        Gracefully stops this thread. Will finish the currently processing
        event before stopping.
        """
        self.terminate = True


class ZMQPlugin(object):
    bus = None

    def __init__(self, bus):
        self.zmqthread = ZMQThread(bus)

        bus.subscribe('start', self.zmqthread.start)
        bus.subscribe('stop', self.zmqthread.stop)
        bus.subscribe('zmq_message', self.print_message)


    def print_message(self, msg):
        girder.logprint.info("Recieved: {}".format(msg))



from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import EchoWebSocket

from girder.api.rest import Resource, filtermodel
from girder.api.describe import Description, describeRoute


class WebSocketAPIEndpoint(Resource):
    def __init__(self):
        super(WebSocketAPIEndpoint, self).__init__()
        self.resourceName = 'ws'
        self.route('GET', (), self.test)

    @describeRoute(
        Description('Test out websockets')
        .param('Upgrade', 'header', default='websocket', paramType='header')
        .param('Connection', 'header', default='upgrade', paramType='header'))
    def test(self, params):
        handler = cherrypy.request.ws_handler
        return 'Test'

def load(info):
    info['zmqplugin'] = ZMQPlugin(cherrypy.engine)

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    info['apiRoot'].ws = WebSocketAPIEndpoint()
    cherrypy.config.update({'/ws': {'tools.websocket.on': True,
                                    'tools.websocket.handler_cls': EchoWebSocket}})
