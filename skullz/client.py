import logging
import zmq
import conf
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
def start():
    ctx = zmq.Context()
    my_conf = conf.getConfig()
    log.info("Starting %s (ctx:%s)"%(__name__,ctx))
    socket = ctx.socket(zmq.REQ)
    front_end_connect = my_conf.get("Client","front_end_connect")
    log.info("Opening socket (%s) towards broker at %s"%(socket,front_end_connect))
    socket.connect(front_end_connect)
    
    for i in range(10):
        socket.send(b"LOL:%s"%i)
        message = socket.recv()
        log.info("Received:\n%s"%message)




if __name__ =='__main__':
    start()
