import logging
import zmq
import conf
import subprocess
import socket
import fcntl
import struct
import sys


log = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


class Service(object):

    def __init__(self):
        self.ctx = zmq.Context()
        log.info("Starting %s (ctx:%s)"%(__name__,self.ctx))
        self.my_conf = conf.getConfig()

    def announce(self):
        announce = self.ctx.socket(zmq.PUSH)
        server_connect = self.my_conf.get("Service","server_connect")
        my_address_iface = self.my_conf.get("Service","announce_interface")
        my_address = get_ip_address(my_address_iface)
        log.info('Announcing to server %s as %s'%(server_connect,my_address))
        announce.connect(server_connect)
        announce.send("UP!%s"%my_address)

    def unannounce(self):
        announce = self.ctx.socket(zmq.PUSH)
        server_connect = self.my_conf.get("Service","server_connect")
        my_address_iface = self.my_conf.get("Service","announce_interface")
        my_address = get_ip_address(my_address_iface)
        log.info('Disannaouncing to server %s as %s'%(server_connect,my_address))
        announce.connect(server_connect)
        announce.send("DOWN!%s"%my_address)


    def start(self):
        socket = self.ctx.socket(zmq.REP)
        service_address = self.my_conf.get("Service","service_default_bind_address")
        log.debug("Serving at %s"%service_address)
        socket.bind(service_address)
        log.debug("Start serving")
        while True:
            message = socket.recv()
            log.debug("Message received: %s"%message)
            command = self.my_conf.get("Service","command")
            command_list = command.split(" ")
            log.debug("Execution of: %s"%command_list)
            cmd = subprocess.Popen(command_list,stdout=subprocess.PIPE)
            socket.send(b"|%s|"%cmd.stdout.read())



def start():
    service = Service()
    try:
        service.announce()
        service.start()
    except KeyboardInterrupt:
        log.info("Shutting down")
        service.unannounce()
        sys.exit(0)

if __name__ =='__main__':
    start()
