
import functools, logging, re
from flask import request, session
from flask_socketio import SocketIO, emit
from peewee import DoesNotExist

from .config import config
from .bus import bus
from .db import ModelError
from . import core
from . import dispenser
from . import wifi
from . import audio
from . import alerts

from .models.Drink import Drink
from .models.DrinkIngredient import DrinkIngredient
from .models.DrinkOrder import DrinkOrder
from .models.Glass import Glass
from .models.Ingredient import Ingredient
from .models.Pump import Pump
from .models.User import User


_shutdownEventPattern = re.compile(r"POWER-REQUEST")

_booleanPattern = re.compile(r"(i?)(true|false|yes|no)")
_intPattern = re.compile(r"-?\d+$")
_floatPattern = re.compile(r"-?\d*\.\d+$")


socket = SocketIO()
_logger = logging.getLogger('Socket')
_consoleSessionId = None


def success(d = None, **kwargs):
    out = {'error': False, **kwargs}
    if type(d) is dict:
        out = {**out, **d}
    return out
#    return {'error': False}

def error(msg):
    return {'error': str(msg)}

def userLoggedIn():
    return 'user' in session

def userIsAdmin():
    return 'user' in session and session['user'].isAdmin

def checkAdmin(clientOpt):
    b = config.getboolean('client', clientOpt)
    return userIsAdmin() if b else True
    
def requireUser(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if userLoggedIn():
            return f(*args, **kwargs)
        else:
            return error('Permission denied!')
    return wrapped
    
def requireAdmin(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if userIsAdmin():
            return f(*args, **kwargs)
        else:
            return error('Permission denied!')
    return wrapped
    
@socket.on_error_default  # handles all namespaces without an explicit error handler
def _socket_default_error_handler(e):
    _logger.exception(e)
    return error('An internal error has ocurred!')
    
#================================================================
# socket events
# These events represent the client-side API
#

#-------------------------------
# special
#
    
@socket.on('connect')
def _socket_connect():
    global _consoleSessionId
    _logger.info('Connection opened from ' + request.remote_addr)
    emit('clientOptions', _buildClientOptions())
    drinkOrder = dispenser.drinkOrder
    if drinkOrder:
        drinkOrder = drinkOrder.toDict(drink = True, glass = True)
    emit('dispenser_state', {'state': dispenser.state, 'order': drinkOrder})
    emit('dispenser_glass', dispenser.glass)
    emit('dispenser_parentalCode', True if dispenser.getParentalCode() else False)
    emit('pumps', [pump.toDict(ingredient = True) for pump in Pump.getAllPumps()])
    emit('pumps_flushing', Pump.flushing)
    emit('wifi_state', wifi.state)
    emit('alerts_changed', alerts.getAll())
    bus.emit('socket/connect', request)
    if request.remote_addr == '127.0.0.1':
        newConnect = _consoleSessionId != request.sid
        _consoleSessionId = request.sid
        emit('audio_volume', audio.getVolume())
        if newConnect:
            bus.emit('socket/consoleConnect')

@socket.on('disconnect')
def _socket_disconnect():
    global _consoleSessionId
    _logger.info('Connection closed from ' + request.remote_addr)
    bus.emit('socket/disconnect', request)
    if request.sid == _consoleSessionId:
        _consoleSessionId = None
        bus.emit('socket/consoleDisconnect')

@socket.on('login')
def _socket_login(params):
    user = User.authenticate(params['name'], params['password'])
    if not user:
        return error('Login failed')
    else:
        session['user'] = user
        bus.emit('socket/userLoggedIn', user)
        return success(user = user.toDict())
        
@socket.on('logout')
def _socket_logout():
    if 'user' in session:
        bus.emit('socket/userLoggedOut', session['user'])
        del session['user']
    return success()

@socket.on('core_restartX')
def _socket_restartX():
    if not checkAdmin('restartXRequiresAdmin'):
        return error('Permission denied!')
    _logger.info('Client requested restart X')
    try:
        core.restartX()
        return success()
    except core.CoreError as e:
        return error(e)

@socket.on('core_restart')
def _socket_restart():
    if not checkAdmin('restartRequiresAdmin'):
        return error('Permission denied!')
    _logger.info('Client requested restart')
    try:
        core.restart()
        return success()
    except core.CoreError as e:
        return error(e)

@socket.on('core_shutdown')
def _socket_shutdown():
    if not checkAdmin('shutdownRequiresAdmin'):
        return error('Permission denied!')
    _logger.info('Client requested shutdown')
    try:
        core.shutdown()
        return success()
    except core.CoreError as e:
        return error(e)

@socket.on('audio_setVolume')
def _socket_audio_setVolume(volume):
    audio.setVolume(float(volume))
    return success()


@socket.on('dispenser_startSetup')
def _socket_dispenser_startSetup():
    if not checkAdmin('dispenserSetupRequiresAdmin'):
        return error('Permission denied!')
    dispenser.startSetup()
    return success()
    
@socket.on('dispenser_stopSetup')
def _socket_dispenser_stopSetup():
    dispenser.stopSetup()
    return success()
        
@socket.on('dispenser_startHold')
def _socket_dispenser_startHold():
    try:
        dispenser.startHold()
        return success()
    except dispenser.DispenserError as e:
        return error(e)

@socket.on('dispenser_stopHold')
def _socket_dispenser_stopHold():
    try:
        dispenser.stopHold()
        return success()
    except dispenser.DispenserError as e:
        return error(e)

@socket.on('dispenser_startDispense')
def _socket_dispenser_startDispense():
    try:
        dispenser.startDispense()
        return success()
    except dispenser.DispenserError as e:
        return error(e)

@socket.on('dispenser_stopDispense')
def _socket_dispenser_stopDispense():
    try:
        dispenser.stopDispense()
        return success()
    except dispenser.DispenserError as e:
        return error(e)
        
@socket.on('dispenser_setControl')
def _socket_dispenser_setControl(ctl):
    dispenser.setControl(ctl)
    return success()
    
@socket.on('dispenser_startPump')
def _socket_dispenser_startPump(params):
    try:
        dispenser.startPump(params)
        return success()
    except dispenser.DispenserError as e:
        return error(e)
    
@socket.on('dispenser_stopPump')
def _socket_dispenser_stopPump():
    try:
        dispenser.stopPump()
        return success()
    except dispenser.DispenserError as e:
        return error(e)

@socket.on('dispenser_setParentalCode')
def _socket_dispenser_setParentalCode(code):
    dispenser.setParentalCode(code)
    return success()
    
@socket.on('dispenser_validateParentalCode')
def _socket_dispenser_validateParentalCode(code):
    if dispenser.validateParentalCode(code):
        return success()
    else:
        return error('Invalid Parental Code')
    
@socket.on('dispenser_submitDrinkOrder')
def _socket_dispenser_submitDrinkOrder(item):
    item['sessionId'] = request.sid
    try:
        dispenser.submitDrinkOrder(item)
        return success()
    except DoesNotExist:
        return error('Drink not found!')
    except dispenser.DispenserError as e:
        return error(e)

@socket.on('dispenser_cancelDrinkOrder')
def _socket_dispenser_cancelDrinkOrder(id):
    try:
        dispenser.cancelDrinkOrder(id)
        return success()
    except DoesNotExist:
        return error('Drink order not found!')
        
@socket.on('dispenser_toggleDrinkOrderHold')
def _socket_dispenser_toggleDrinkOrderHold(id):
    try:
        dispenser.toggleDrinkOrderHold(id)
        return success()
    except DoesNotExist:
        return error('Drink order not found!')
        
@socket.on('wifi_getNetworks')
def _socket_wifi_getNetworks():
    return success(networks = wifi.getNetworks())
    
@socket.on('wifi_connectToNetwork')
def _socket_wifi_connectToNetwork(params):
    wifi.connectToNetwork(params)
    return success()
    
@socket.on('wifi_disconnectFromNetwork')
def _socket_wifi_disconnectFromNetwork(ssid):
    wifi.disconnectFromNetwork(ssid)
    return success()
    
@socket.on('wifi_forgetNetwork')
def _socket_wifi_forgetNetwork(ssid):
    wifi.forgetNetwork(ssid)
    return success()
    
@socket.on('getGlasses')
def _socket_getGlasses():
    return success(items = [g.toDict() for g in Glass.select()])

@socket.on('getGlass')
def _socket_getGlass(id):
    try:
        g = Glass.get(Glass.id == id)
        return success(item = g.toDict(drinks = True))
    except DoesNotExist:
        return error('Glass not found!')
    
@socket.on('saveGlass')
def _socket_saveGlass(item):
    try:
        Glass.saveFromDict(item)
        return success()
    except ModelError as e:
        return error(e)

@socket.on('deleteGlass')
def _socket_deleteGlass(id):
    try:
        Glass.deleteById(id)
        return success()
    except DoesNotExist:
        return error('Glass not found!')
    except ModelError as e:
        return error(e)
         
@socket.on('getIngredients')
def _socket_getIngredients():
    return success(items = [i.toDict() for i in Ingredient.select()])

@socket.on('getIngredient')
def _socket_getIngredient(id):
    try:
        i = Ingredient.get(Ingredient.id == id)
        return success(item = i.toDict(drinks = True))
    except DoesNotExist:
        return error('Ingredient not found!')
    
@socket.on('saveIngredient')
def _socket_saveIngredient(item):
    try:
        Ingredient.saveFromDict(item)
        return success()
    except ModelError as e:
        return error(e)

@socket.on('deleteIngredient')
def _socket_deleteIngredient(id):
    try:
        Ingredient.deleteById(id)
        return success()
    except DoesNotExist:
        return error('Ingredient not found!')
    except ModelError as e:
        return error(e)

@socket.on('getDrinks')
def _socket_getDrinks():
    return success(items = [d.toDict(ingredients = True) for d in Drink.select()])
    
@socket.on('getDrink')
def _socket_getDrink(id):
    try:
        d = Drink.get(Drink.id == id)
        return success(item = d.toDict(glass = True, ingredients = True))
    except DoesNotExist:
        return error('Drink not found!')
    
@socket.on('saveDrink')
def _socket_saveDrink(item):
    try:
        Drink.saveFromDict(item)
        return success()
    except DoesNotExist:
        return error('Drink not found!')
    except ModelError as e:
        return error(e)

@socket.on('deleteDrink')
def _socket_deleteDrink(id):
    try:
        Drink.deleteById(id)
        return success()
    except DoesNotExist:
        return error('Drink not found!')
    except ModelError as e:
        return error(e)
         
@socket.on('getDrinksMenu')
def _socket_getDrinksMenu():
    return success(items = [d.toDict() for d in Drink.getMenuDrinks()])
    
@socket.on('getWaitingDrinkOrders')
def _socket_getWaitingDrinkOrders():
    return success(items = [do.toDict(drink = True) for do in DrinkOrder.getWaiting()])

@socket.on('getDrinkOrder')
def _socket_getDrinkOrder(id):
    try:
        o = DrinkOrder.get(DrinkOrder.id == id)
        return success(item = o.toDict(drink = True))
    except DoesNotExist:
        return error('Drink order not found!')
    
@socket.on('getPumps')
def _socket_getPumps():
    return success(items = [p.toDict(ingredient = True) for p in Pump.select()])
    
@socket.on('loadPump')
def _socket_loadPump(params):
    try:
        Pump.loadPump(params)
        return success()
    except DoesNotExist:
        return error('Pump not found!')
    except ModelError as e:
        return error(e)

@socket.on('unloadPump')
def _socket_unloadPump(id):
    try:
        Pump.unloadPump(id)
        return success()
    except DoesNotExist:
        return error('Pump not found!')
    except ModelError as e:
        return error(e)
    
@socket.on('primePump')
def _socket_primePump(params):
    try:
        Pump.primePump(params, useThread = True)
        return success()
    except DoesNotExist:
        return error('Pump not found!')
    except ModelError as e:
        return error(e)
    
@socket.on('drainPump')
def _socket_drainPump(id):
    try:
        Pump.drainPump(id, useThread = True)
        return success()
    except DoesNotExist:
        return error('Pump not found!')
    except ModelError as e:
        return error(e)

@socket.on('cleanPump')
def socket_cleanPump(params):
    try:
        Pump.cleanPump(params, useThread = True)
        return success()
    except DoesNotExist:
        return error('Pump not found!')
    except ModelError as e:
        return error(e)

@socket.on('startFlushingPumps')
def socket_startFlushingPumps(ids):
    try:
        Pump.startFlush(ids)
        return success()
    except ModelError as e:
        return error(e)
        
@socket.on('stopFlushingPumps')
def socket_stopFlushingPumps():
    try:
        Pump.stopFlush()
        return success()
    except ModelError as e:
        return error(e)
        
@socket.on('alerts_clear')
def socket_alerts_clear():
    alerts.clear()
    return success()
    
    
    
#================================================================
# bus events
#
    
#-------------------------------
# misc
#
    
@bus.on('config/reloaded')
def _but_config_reloaded():
    socket.emit('clientOptions', _buildClientOptions())
    
@bus.on('serial/event')
def _bus_serial_event(e):
    if _consoleSessionId:
        m = _shutdownEventPattern.match(e)
        if m:
            _logger.debug('Got shutdown request')
            socket.emit('shutdownRequest', room = _consoleSessionId)
    
#-------------------------------
# alert
#
    
@bus.on('alerts/add')
@bus.on('alerts/clear')
def _bus_alerts():
    try:
        socket.emit('alerts_changed', alerts.getAll())
    except:
        pass
    
#-------------------------------
# dispenser
#

@bus.on('dispenser/state')
def _bus_dispenser_state(state, drinkOrder):
    if drinkOrder:
        drinkOrder = drinkOrder.toDict(drink = True, glass = True)
    socket.emit('dispenser_state', {'state': state, 'drinkOrder': drinkOrder})
    
@bus.on('dispenser/glass')
def _bus_dispenser_glass(ready):
    socket.emit('dispenser_glass', ready)

@bus.on('dispenser/parentalCode')
def _bus_dispenser_parentalCode(locked):
    socket.emit('dispenser_parentalCode', locked)
    
#-------------------------------
# wifi
#

@bus.on('wifi/state')
def _bus_wifi_state(state):
    socket.emit('wifi_state', state)
    
#-------------------------------
# audio
#
    
@bus.on('audio/playFile')
def _bus_audio_playFile(file, console, sessionId, broadcast):
    if broadcast:
        _logger.debug('Play {} everywhere'.format(file))
        socket.emit('audio_playFile', file)
    else:
        if sessionId:
            _logger.debug('Play {} on client {}'.format(file, sessionId))
            socket.emit('audio_playFile', file, room = sessionId)
        elif console and _consoleSessionId:
            _logger.debug('Play {} on console'.format(file))
            socket.emit('audio_playFile', file, room = _consoleSessionId)

@bus.on('audio/volume')
def _bus_audio_volume(volume):
    if _consoleSessionId:
        socket.emit('audio_volume', volume, room = _consoleSessionId)
        
#-------------------------------
# glass
#

@bus.on('model/glass/saved')
def _bus_modelGlassSaved(g):
    socket.emit('glassSaved', g.toDict())

@bus.on('model/glass/deleted')
def _bus_modelGlassDeleted(g):
    socket.emit('glassDeleted', g.toDict())

#-------------------------------
# ingredient
#
            
@bus.on('model/ingredient/saved')
def _bus_modelIngredientSaved(i):
    socket.emit('ingredientSaved', i.toDict())

@bus.on('model/ingredient/deleted')
def _bus_modelIngredientDeleted(i):
    socket.emit('ingredientDeleted', i.toDict())
                 
#-------------------------------
# drink
#

@bus.on('model/drink/saved')
def _bus_modelDrinkSaved(d):
    socket.emit('drinkSaved', d.toDict(glass = True, ingredients = True))

@bus.on('model/drink/deleted')
def _bus_modelDrinkDeleted(d):
    socket.emit('drinkDeleted', d.toDict())
    
#-------------------------------
# drink order
#

@bus.on('model/drinkOrder/saved')
def _bus_modelDrinkOrderSaved(o):
    socket.emit('drinkOrderSaved', o.toDict(drink = True))

@bus.on('model/drinkOrder/deleted')
def _bus_modelDrinkOrderDeleted(o):
    socket.emit('drinkOrderDeleted', o.toDict())
         
#-------------------------------
# pump
#
    
@bus.on('model/pump/saved')
def _bus_modelPumpSaved(p):
    socket.emit('pumpSaved', p.toDict(ingredient = True))

@bus.on('model/pump/setup')
def _bus_modelPumpSetup():
    socket.emit('pumps_setup', Pump.setup)

@bus.on('model/pump/flushing')
def _bus_modelPumpFlushing():
    socket.emit('pumps_flushing', Pump.flushing)


    
def _buildClientOptions():
    opts = dict(config.items('client'))
    for k, v in opts.items():
        if _booleanPattern.match(v):
            opts[k] = config.getboolean('client', k)
        elif _intPattern.match(v):
            opts[k] = config.getint('client', k)
        elif _floatPattern.match(v):
            opts[k] = config.getfloat('client', k)
    return opts
            
