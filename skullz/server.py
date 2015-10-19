import logging
import zmq
import conf
import subprocess
import threading
import time
import sys

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

UP_MESSAGE = "UP!"
DOWN_MESSAGE = "DOWN!"

process_registerer_address = "ipc://address_list"
front_end_process_dealer = "ipc://pront_end_process_dealer"

class Server(object):
    def __init__(self):
        self.ctx = zmq.Context()
        log.info("Starting %s (ctx:%s)"%(__name__,self.ctx))
        self.my_conf = conf.getConfig()


    def process_registerer(self):
        '''
        Function for the service registering thread

        -- BUG: anyone can (un)subscribe a service!

        -- BUG: if the server goes down, you have to restart all the clients
            (this one is easy!)
        '''
        address_list = set()
        service_registry_subscriber = self.ctx.socket(zmq.PULL)
        announce_bind = self.my_conf.get("Syndacation","announce_bind")
        log.debug("Binding to subscriber endpoint at %s"%announce_bind)
        service_registry_subscriber.bind(announce_bind)
        register_addresses = self.ctx.socket(zmq.REP)
        register_addresses.bind(process_registerer_address)
        poller = zmq.Poller()
        poller.register(service_registry_subscriber,zmq.POLLIN)
        poller.register(register_addresses,zmq.POLLIN)

        while True:
            log.debug("Current addresses: %s"%address_list)
            socks = dict(poller.poll())
            if service_registry_subscriber in socks:
                message = service_registry_subscriber.recv()
                log.debug("Message received: %s"%message)
                if(message.startswith(UP_MESSAGE)):
                    #register message as service
                    log.debug("registering new service: %s"%message)
                    address_list.add(message[len(UP_MESSAGE):])
                if(message.startswith(DOWN_MESSAGE)):
                    #unregister by name
                    log.debug("unregistering  service: %s"%message)
                    address_list.remove(message[len(DOWN_MESSAGE):])
            if register_addresses in socks:
                answer = "|".join(address_list)
                log.debug("Got addresses request: answer is %s"%answer)
                register_addresses.recv()
                register_addresses.send(answer)




    def serve(self):
        socket = self.ctx.socket(zmq.REP)
        #front_end_bind = self.my_conf.get("Syndacation","front_end_bind")
        #socket.bind(front_end_bind)
        socket.connect(front_end_process_dealer)
        while True:
            message = socket.recv()
            log.debug("Message received: %s"%message)
            cmd = self.ask_others(message)
            socket.send(b"|%s|"%cmd)

    def ask_one(self,address,message):
        log.debug("Asking to address %s"%address)
        a_service_socket = self.ctx.socket(zmq.REQ)
        a_service_socket.connect("tcp://%s:5561"%address)
        a_service_socket.send("HELO:%s"%message)
        cmd = a_service_socket.recv()
        return cmd
        
    
    def ask_others(self,message):
        log.debug("Asking Other services")
        register = self.ctx.socket(zmq.REQ)
        register.connect(process_registerer_address)
        register.send('');
        addresses_string = register.recv()
        addresses = [x.strip() for x in addresses_string.split(',')]
        log.debug("Received addresses:\n%s"%addresses)
        future_list = list()
        if(addresses[0]!=''):
            for address in addresses:
                log.debug("Creating request for :%s"%address)
                future_list.append(self.ask_one(address,message))
        log.debug("Collecting answers for requests")
        results = future_list
        return results





    def start(self):
        log.debug("Start serving threads")
        serving_threads = self.my_conf.get("Syndacation","serving_threads")
        log.debug("Starting %s serving threads"%serving_threads)
        for i in range(int(serving_threads)):
            serving_thread=threading.Thread(target=self.serve,name="serving_thread-%s"%i)
            #serving_thread = threading.Thread(target=self.serve,name="serving_thread")
            serving_thread.setDaemon(True)
            serving_thread.start()
        process_register_thread = threading.Thread(target=self.process_registerer,name="process_register_thread")
        process_register_thread.setDaemon(True)
        process_register_thread.start()
        #Starting device
        front_end_router = self.ctx.socket(zmq.ROUTER)
        front_end_bind = self.my_conf.get("Syndacation","front_end_bind")
        log.debug("Binding ROUTER at %s "%front_end_bind)
        front_end_router.bind(front_end_bind)
        front_end_dealer = self.ctx.socket(zmq.DEALER)
        log.debug("Binding DEALER at %s "%front_end_process_dealer)
        front_end_dealer.bind(front_end_process_dealer)
        log.debug("Creating QUEUE device")
        zmq.device(zmq.QUEUE,front_end_router,front_end_dealer)




def start():
    try:
        s = Server()
        s.start()
        while threading.active_count() > 0:
            time.sleep(0.1)
    except KeyboardInterrupt:
        log.info("Exiting")
        sys.exit(0)

if __name__ =='__main__':
    start()

