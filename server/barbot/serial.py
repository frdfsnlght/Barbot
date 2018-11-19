
import logging, serial, re, time
from threading import Thread, Event, Lock

from .config import config
from .bus import bus
from . import alerts


_messagePattern = re.compile(r"#(.*)")
_errorPattern = re.compile(r"!(.*)")
_eventPattern = re.compile(r"\*(.*)")

_logger = logging.getLogger('Serial')
_exitEvent = Event()
_thread = None
_port = None
_writeLock = Lock()
_responseReceived = Event()
_responseError = None
_responseLines = []


class SerialError(Exception):
    pass
    
@bus.on('server/start1')
def _bus_serverStart():
    global _thread, _port
    
    try:
        _port = serial.Serial(config.get('serial', 'port'), config.getint('serial', 'speed'), timeout = None)
        _logger.info('Serial port {} opened at {}'.format(_port.name, _port.baudrate))
    except IOError as e:
        _logger.error(str(e))
        _logger.info('Serial port {} could not be opened'.format(config.get('serial', 'port')))
        alerts.add('Serial port could not be opened!')
        return
    
    _exitEvent.clear()
    _thread = Thread(target = _threadLoop, name = 'SerialThread')
    _thread.daemon = True
    _thread.start()
    
    try:
        write('C?')
    except SerialError as e:
        _logger.error(e)
    
@bus.on('server/stop')
def _bus_serverStop():
    _exitEvent.set()
    
def _threadLoop():
    global _port
    _logger.info('Serial thread started')
    try:
        while not _exitEvent.is_set():
            _readPort()
    except Exception as e:
        _logger.exception(str(e))
    finally:
        _port.close()
        _port = None
    _logger.info('Serial thread stopped')
    alerts.add('Serial thread stopped!')
    
def _readPort():
    line = _port.readline()
    if line:
        _processLine(line.rstrip().decode('ascii'))

def _processLine(line):
    _logger.debug('Receive: {}'.format(line))
    
    if line.lower() == 'ok':
        _responseError = None
        _responseReceived.set()
        return
        
    m = _errorPattern.match(line)
    if m:
        _responseError = m.group(1)
        _responseReceived.set()
        return
        
    m = _eventPattern.match(line)
    if m:
        bus.emit('serial/event', m.group(1))
        return
        
    m = _messagePattern.match(line)
    if m:
        _logger.info('Message: {}'.format(m.group(1)))
        return
        
    _responseLines.append(line)
    
def write(cmd, timeout = 5):
    global _responseLines, _responseError
    with _writeLock:
        _logger.debug('Send: {}'.format(cmd))
        if not _port:
            raise SerialError('Serial port is not open!')
            
        _responseLines = []
        _responseError = None
        _responseReceived.clear()
        buf = cmd.encode('ascii')
        
        if cmd[0].isupper():
            cs = 0
            for c in buf:
                cs = cs ^ c
            buf = buf + b'~' + '{:02X}'.format(cs).encode('ascii')

        _logger.debug('Writing {}'.format(buf))
        
        _port.write(buf + b'\r\n')
        
        if timeout:
            if not _responseReceived.wait(timeout):
                _responseError = 'timeout'
        else:
            _responseReceived.wait()
                
        if _responseError:
            raise SerialError(_responseError)
            
        return _responseLines
   
