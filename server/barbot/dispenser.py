
import logging, os, datetime, time, re, random
from threading import Thread, Event

from .bus import bus
from .config import config
from .db import db, ModelError
from . import serial
from . import utils
from .models.Drink import Drink
from .models.DrinkOrder import DrinkOrder
from .models.DrinkIngredient import DrinkIngredient
from .models.Pump import Pump, anyPumpsRunning

    
ST_WAIT = 'wait'
ST_PAUSE = 'pause'
ST_HOLD = 'hold'
ST_DISPENSE = 'dispense'

ST_DISPENSE_START = 'start'
ST_DISPENSE_RUN = 'run'
ST_DISPENSE_PICKUP = 'pickup'
ST_DISPENSE_CLEAR_GLASS = 'clear_glass'
ST_DISPENSE_CLEAR_CANCEL = 'clear_cancel'

CTL_START = 'start'
CTL_CANCEL = 'cancel'
CTL_OK = 'ok'


_sensorEventPattern = re.compile(r"(?i)S(\d)(\d)")

_logger = logging.getLogger('Dispenser')
_exitEvent = Event()
_thread = None
_requestPause = False
_requestDispense = False
_requestHold = False
_dispenserEvent = Event()
_lastDrinkOrderCheckTime = time.time()
_lastIdleAudioCheckTime = time.time()
_control = None
_pump = None

glassReady = False
state = ST_WAIT
drinkOrder = None


class DispenserError(Exception):
    pass

@bus.on('server/start')
def _bus_serverStart():
    global _thread
    _exitEvent.clear()
    _thread = Thread(target = _threadLoop, name = 'DispenserThread', daemon = True)
    _thread.start()

@bus.on('server/stop')
def _bus_serverStop():
    _exitEvent.set()

@bus.on('socket/consoleConnect')
def _bus_consoleConnect():
    _resetTimers()
    
@bus.on('serial/event')
def _bus_serialEvent(e):
    global glassReady
    m = _sensorEventPattern.match(e)
    if m and m.group(1) == '0':
        newGlassReady = m.group(2) == '1'
        if newGlassReady != glassReady:
            glassReady = newGlassReady
            bus.emit('dispenser/glassReady', glassReady)
            _dispenserEvent.set()
            
#-----------------
# TODO: remove this temp code someday
glassThread = None
import os.path
@bus.on('server/start')
def _bus_startGlassThread():
    global glassThread
    glassThread = Thread(target = _glassThreadLoop, name = 'BarbotGlassThread', daemon = True)
    glassThread.start()
def _glassThreadLoop():
    global glassReady
    while not _exitEvent.is_set():
        newGlassReady = os.path.isfile(os.path.join(os.path.dirname(__file__), '..', 'var', 'glass'))
        if newGlassReady != glassReady:
            glassReady = newGlassReady
            bus.emit('dispenser/glassReady', glassReady)
            _dispenserEvent.set()
        time.sleep(1)
# end of temp code
#---------------------
    
def startPause():
    global _requestPause
    _requestPause = True
    
def stopPause():
    global _requestPause
    _requestPause = False

def startDispense():
    global _requestDispense
    _requestDispense = True
    
def stopDispense():
    global _requestDispense
    _requestDispense = False

def startHold():
    global _requestHold
    _requestHold = True
    
def stopHold():
    global _requestHold
    _requestHold = False

def setControl(ctl):
    global _control
    _control = ctl
    _dispenserEvent.set()
        
def startPump(id):
    global _pump
    if state != ST_DISPENSE:
        raise DispenserError('Invalid dispenser state!')
    if _pump:
        stopPump()
    _pump = Pump.get_or_none(Pump.id == id)
    if not _pump:
        raise ValueError('Invalid pump Id!')
    # TODO: call pump method to start pumping
    _logger.debug('startPump {}'.format(id))

def stopPump():
    global _pump
    if not _pump: return
    # TODO: call pump method to stop pumping
    _logger.debug('stopPump {}'.format(_pump.id))
    _pump = None

def _threadLoop():
    global _lastDrinkOrderCheckTime, state
    _logger.info('Dispenser thread started')
    try:
        while not _exitEvent.is_set():
        
            if _requestPause:
                state = ST_PAUSE
                bus.emit('dispenser/state', state, None)
                while _requestPause and not _exitEvent.is_set():
                    _checkIdle()
                    time.sleep(1)
                state = ST_WAIT
                bus.emit('dispenser/state', state, None)

            if _requestDispense:
                state = ST_DISPENSE
                bus.emit('dispenser/state', state, None)
                while _requestDispense and not _exitEvent.is_set():
                    time.sleep(1)
                state = ST_WAIT
                bus.emit('dispenser/state', state, None)
                
            if _requestHold:
                state = ST_HOLD
                bus.emit('dispenser/state', state, None)
                while _requestHold and not _exitEvent.is_set():
                    _checkIdle()
                    time.sleep(1)
                state = ST_WAIT
                bus.emit('dispenser/state', state, None)
                
            if not _exitEvent.is_set():
                t = time.time()
            
                if (t - _lastDrinkOrderCheckTime) > config.getfloat('dispenser', 'drinkOrderCheckInterval'):
                    _lastDrinkOrderCheckTime = t
                    o = DrinkOrder.getFirstPending()
                    if o:
                        _dispenseDrinkOrder(o)
                        _resetTimers()
                        continue

                _checkIdle()
                time.sleep(1)
    except Exception as e:
        _logger.exception(str(e))
    _logger.info('Dispenser thread stopped')

def _resetTimers():
    global _lastDrinkOrderCheckTime, _lastIdleAudioCheckTime
    t = time.time()
    _lastDrinkOrderCheckTime = t
    _lastIdleAudioCheckTime = t
   
def _checkIdle():
    global _lastIdleAudioCheckTime
    if (time.time() - _lastIdleAudioCheckTime) > config.getfloat('dispenser', 'idleAudioInterval'):
        _lastIdleAudioCheckTime = time.time()
        if random.random() <= config.getfloat('dispenser', 'idleAudioChance'):
            bus.emit('audio/play', 'idle', console = True)
    
def _dispenseDrinkOrder(o):
    global state, drinkOrder, _control
    state = ST_DISPENSE_START
    drinkOrder = o
    _logger.info('Preparing to dispense {}'.format(drinkOrder.desc()))
    
    # this gets the drink out of the queue
    drinkOrder.startedDate = datetime.datetime.now()
    drinkOrder.save()
    
    # wait for user to start or cancel the order
    
    _dispenserEvent.clear()
    _control = None
    
    bus.emit('dispenser/state', state, drinkOrder)
    bus.emit('lights/play', 'waitForDispense')
    bus.emit('audio/play', 'waitForDispense', console = True)
    
    while True:
        _dispenserEvent.wait()
        _dispenserEvent.clear()
        
        # glassReady or _control changed
        
        if _control == CTL_CANCEL:
            _logger.info('Cancelled dispensing {}'.format(drinkOrder.desc()))
            drinkOrder.placeOnHold()
            bus.emit('audio/play', 'cancelledDispense', console = True)
            bus.emit('audio/play', 'drinkOrderOnHold', sessionId = drinkOrder.sessionId)
            drinkOrder = None
            state = ST_WAIT
            _resetTimers()
            bus.emit('dispenser/state', state, drinkOrder)
            bus.emit('lights/play', None)
            return
        
        if _control == CTL_START and glassReady:
            state = ST_DISPENSE_RUN
            _logger.info('Starting to dispense {}'.format(drinkOrder.desc()))
            bus.emit('dispenser/state', state, drinkOrder)
            bus.emit('audio/play', 'startDispense', console = True)
            bus.emit('lights/play', 'startDispense')
            break
    
    drink = drinkOrder.drink
    _control = None
    
    for step in sorted({i.step for i in drink.ingredients}):
    
        ingredients = [di for di in drink.ingredients if di.step == step]
        _logger.info('Executing step {}, {} ingredients'.format(step, len(ingredients)))
        pumps = []
        
        # start the pumps
        for di in ingredients:
            ingredient = di.ingredient
            pump = ingredient.pump.first()
            amount = utils.toML(di.amount, di.units)
            pump.forward(amount)
            ingredient.timesDispensed = ingredient.timesDispensed + 1
            ingredient.amountDispensed = ingredient.amountDispensed + amount
            ingredient.save()
            pumps.append(pump)
            
        # wait for the pumps to stop, glass removed, order cancelled
        
        while True and state == ST_DISPENSE_RUN:
            if not pumps[-1].running:
                pumps.pop()
            if not len(pumps):
                # all pumps have stopped
                break

            if _dispenserEvent.wait(0.1):
                _dispenserEvent.clear()
                
                if not glassReady:
                    _logger.warning('Glass removed while dispensing {}'.format(drinkOrder.desc()))
                    for pump in pumps:
                        pump.stop()
                    bus.emit('audio/play', 'glassRemovedDispense', console = True)
                    bus.emit('audio/play', 'drinkOrderOnHold', sessionId = drinkOrder.sessionId)
                    drinkOrder.placeOnHold()
                    drinkOrder = None
                    state = ST_DISPENSE_CLEAR_GLASS
                    bus.emit('dispenser/state', state, drinkOrder)
                    bus.emit('lights/play', 'glassRemovedDispense')

                if _control == CTL_CANCEL:
                    _logger.info('Cancelled dispensing {}'.format(drinkOrder.desc()))
                    for pump in pumps:
                        pump.stop()
                    bus.emit('audio/play', 'cancelledDispense', console = True)
                    bus.emit('audio/play', 'drinkOrderOnHold', sessionId = drinkOrder.sessionId)
                    drinkOrder.placeOnHold()
                    drinkOrder = None
                    state = ST_DISPENSE_CLEAR_CANCEL
                    bus.emit('dispenser/state', state, drinkOrder)
                    bus.emit('lights/play', None)

        if state != ST_DISPENSE_RUN:
            break
            
        # proceed to next step...
        
    # all done!
    
    if state == ST_DISPENSE_RUN:
        _logger.info('Done dispensing {}'.format(drinkOrder.desc()))
        drink.timesDispensed = drink.timesDispensed + 1
        if not drink.isFavorite and drink.timesDispensed >= config.getint('dispenser', 'favoriteDrinkCount'):
            drink.isFavorite = True
        drink.save()
        drinkOrder.completedDate = datetime.datetime.now()
        drinkOrder.save()
        state = ST_DISPENSE_PICKUP
        bus.emit('dispenser/state', state, drinkOrder)
        bus.emit('audio/play', 'endDispense', console = True)
        bus.emit('audio/play', 'drinkOrderReady', sessionId = dispenseDrinkOrder.sessionId)
        bus.emit('lights/play', 'endDispense')
        
    _dispenserEvent.clear()

    while state is not ST_WAIT:
        if _dispenserEvent.wait(0.5):
            _dispenserEvent.clear()
            if state == ST_DISPENSE_CLEAR_CANCEL or dispenseState == ST_DISPENSE_PICKUP:
                if not glassReady:
                    state = ST_WAIT
                    drinkOrder = None
            elif _control == CTL_OK:
                state = ST_WAIT
                    
    bus.emit('dispenser/state', state, drinkOrder)
    bus.emit('lights/play', None)
    _resetTimers()
    _rebuildMenu()
    
    DrinkOrder.deleteOldCompleted(config.getint('dispenser', 'maxDrinkOrderAge'))
    