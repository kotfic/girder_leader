import zmq
import sys

if __name__ == "__main__":
    context = zmq.Context()
    print 'Connecting to server...'

    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:5555')

    print 'Connected'
    socket.send(" ".join(sys.argv[1:]))

    message = socket.recv()
    print 'Received reply [', message, ']'
