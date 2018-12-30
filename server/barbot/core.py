
import logging, os, time, subprocess

from .bus import bus
from .config import config
from . import serial
from . import dispenser
from .models.Pump import anyPumpsRunning
from .models.Drink import Drink
from .models.Glass import Glass
from .models.Ingredient import Ingredient


_logger = logging.getLogger('Core')
_firstConnect = False


class CoreError(Exception):
    pass

@bus.on('socket/consoleConnect')
def _bus_consoleConnect():
    global _firstConnect
    if not _firstConnect:
        _firstConnect = True
        try:
            serial.write('RO', timeout = 1)  # power on
        except serial.SerialError as e:
            _logger.error(e)
        bus.emit('core/firstConnect')

def getStatistics():
    stats = {
        'drinks': Drink.select().count(),
        'ingredients': Ingredient.select().count(),
        'glasses': Glass.select().count(),
        'menuDrinks': Drink.getMenuDrinksCount(),
        'drinksServed': dispenser.drinksServed,
    }
    
    cmd = config.get('core', 'diskFreeCommand').split(' ')
    cmd = [p if p != '{}' else config.getpath('core', 'diskFreePath') for p in cmd]
    out = subprocess.run(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
    if out.returncode != 0:
        _logger.error('Error trying to get disk free: {}'.format(out.stdout))
    lines = out.stdout.splitlines()
    stats['diskFree'] = float(lines[-1].strip().replace('%', ''))
    
    return stats
            
def restartX():
    cmd = config.get('core', 'restartXCommand').split(' ')
    out = subprocess.run(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
    if out.returncode != 0:
        _logger.error('Error trying to restart X: {}'.format(out.stdout))
        
def restart():
    if dispenser.state == 'setup' or anyPumpsRunning():
        raise CoreError('Unable to restart while in setup or any pumps are running!')

    bus.emit('lights/play', 'restart')
    bus.emit('audio/play', 'restart', console = True)
    time.sleep(config.getfloat('core', 'restartDelay'))
    
    cmd = config.get('core', 'restartCommand').split(' ')
    out = subprocess.run(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
    if out.returncode != 0:
        _logger.error('Error trying to restart: {}'.format(out.stdout))
        
def shutdown():
    if dispenser.state == 'setup' or anyPumpsRunning():
        raise CoreError('Unable to shutdown while in setup or any pumps are running!')
        
    bus.emit('lights/play', 'shutdown')
    bus.emit('audio/play', 'shutdown', console = True)
    
    try:
        serial.write('RT{}'.format(config.get('core', 'shutdownTimer')))
    except serial.SerialError as e:
        _logger.error(e)
    time.sleep(config.getfloat('core', 'shutdownDelay'))
    
    cmd = config.get('core', 'shutdownCommand').split(' ')
    out = subprocess.run(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
    if out.returncode != 0:
        _logger.error('Error trying to shutdown: {}'.format(out.stdout))
    
    

