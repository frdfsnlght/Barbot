#!/usr/bin/python3

import eventlet
eventlet.monkey_patch()

import sys, os, signal, logging, time, argparse
from threading import Thread, Event
from peewee import IntegrityError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import barbot.config

config = barbot.config.load()

import barbot.logging

barbot.logging.configure()
logger = logging.getLogger('Server')

from barbot.bus import bus
import barbot.alerts
import barbot.daemon as daemon
import barbot.serial
import barbot.wifi
import barbot.lights
import barbot.audio
import barbot.dispenser

from barbot.db import initializeDB
import barbot.core

from barbot.app import app
from barbot.socket import socket

webThread = None
exitEvent = Event()


def catchSIGTERM(signum, stackframe):
    logger.info('caught SIGTERM')
    exitEvent.set()
    
def catchSIGINT(signum, stackframe):
    logger.info('caught SIGINT')
    exitEvent.set()
    
def webThreadLoop():
    host = config.get('server', 'listenAddress')
    port = config.get('server', 'listenPort')
    logger.info('Web thread started on ' + host + ':' + port)
    socket.init_app(app, async_mode='eventlet')
    socket.run(
        app,
        host = host,
        port = port,
        debug = config.getboolean('server', 'socketIODebug'),
        use_reloader  = False
    )
    logger.info('Web thread stopped')

def startServer():
    logger.info('Server starting')
    
    initializeDB()

    signal.signal(signal.SIGTERM, catchSIGTERM)
    signal.signal(signal.SIGINT, catchSIGINT)
    
    # start threads
    
    webThread = Thread(target = webThreadLoop, name = 'WebThread')
    webThread.daemon = True
    webThread.start()

    bus.emit('server/start1')
    bus.emit('server/start')
    
    logger.info('Server started')
    
    # wait for the end
    while not exitEvent.is_set():
        exitEvent.wait(1)
        
    bus.emit('server/stop')
    #time.sleep(3)
    
    logger.info('Server stopped')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Barbot server')
    parser.add_argument('cmd', choices = ['start', 'stop', 'restart', 'status', 'debug'],
                        help = 'the command to run')
    args = parser.parse_args()
    
    if args.cmd == 'start':
        daemon.start(startServer)
    elif args.cmd == 'stop':
        daemon.stop()
    elif args.cmd == 'restart':
        daemon.restart(startServer)
    elif args.cmd == 'status':
        args.daemon.status()
    elif args.cmd == 'debug':
        startServer()
    sys.exit(0)

        





