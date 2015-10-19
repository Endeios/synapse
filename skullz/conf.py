from ConfigParser import ConfigParser
import logging
import logging.config


logging_basic_config = """[loggers]
keys=root,simpleExample

[handlers]
keys=consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[logger_simpleExample]
level=DEBUG
handlers=consoleHandler
qualname=simpleExample
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s|%(threadName)s|%(name)s|%(levelname)s|%(message)s
datefmt=

"""

app_config = """[Syndacation]
front_end_bind = tcp://*:5559
announce_bind  = tcp://*:5560
serving_threads = 5

[Service]
server_connect  = tcp://localhost:5560
service_default_bind_address  = tcp://*:5561
announce_interface = eth0

command =ls -l

[Client]
front_end_connect = tcp://localhost:5559

"""

logger = logging.getLogger('Configuration')
logging.basicConfig(level=logging.DEBUG)


from os.path import expanduser
import os

base_dir = expanduser("~/.pirate")


logger.debug("Cheking exsistence of %s"%base_dir)
if not os.path.exists(base_dir):
    logger.warn("No config folder exsis, creating")
    os.makedirs(base_dir+"/")
    logger.warn("Created %s "% base_dir)

logging_conf_path = expanduser("%s/logging.conf"%base_dir)
logger.debug("User conf path is: "+logging_conf_path)

if not os.path.exists(logging_conf_path):
    logger.warn("No logging config file exsis, creating")
    with open(logging_conf_path,"w") as conf_file:
        conf_file.write(logging_basic_config)

logger.debug("Reading logging configuration from %s"% logging_conf_path)

logging.config.fileConfig(logging_conf_path)

def getConfig():
    parser = ConfigParser()
    conf_path = expanduser("%s/sea.conf"%base_dir)
    if not os.path.exists(conf_path):
        logger.warn("No application config file exsis, creating")
        with open(conf_path,"w") as conf_file:
            conf_file.write(app_config)

    logger.debug("Reading configuration from %s"% conf_path)
    parser.read(conf_path)
    return parser

def addService(service):
    config = getConfig()
    pass

def addClient(client):
    config = getConfig()
    pass


