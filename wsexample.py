import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import EchoWebSocket

cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': 9000})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

class Root(object):
    @cherrypy.expose
    def index(self):
        return 'some HTML with a websocket javascript connection'

    @cherrypy.expose
    def ws(self):
        # you can access the class instance through
        import rpdb; rpdb.set_trace()
        handler = cherrypy.request.ws_handler


if __name__ == "__main__":
    cherrypy.quickstart(
        Root(), '/', config={'/ws': {'tools.websocket.on': True,
                                     'tools.websocket.handler_cls': EchoWebSocket}})
