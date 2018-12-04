
import functools, logging, re
from flask import request, session
from flask_socketio import SocketIO, emit
from peewee import DoesNotExist

from .config import config
from .bus import bus
from . import units
from .db import db, ModelError
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


class ValidationError(Exception):
    pass
    
def success(d = None, **kwargs):
    out = {'error': False, **kwargs}
    if type(d) is dict:
        out = {**out, **d}
    return out
#    return {'error': False}

def error(msg):
    return {'error': str(msg)}

#--------------------------------
# decorators
#

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
    
def requireDispenserState(state):
    def wrap(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if dispenser.state == state:
                return f(*args, **kwargs)
            else:
                return error('Invalid dispenser state!')
        return wrapped
    return wrap
        
def validate(rules):
    def wrap(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if isinstance(args[0], dict):
                try:
                    validateParams(args[0], rules)
                    return f(*args, **kwargs)
                except ValidationError as e:
                    return error(e)
            else:
                return f(*args, **kwargs)
        return wrapped
    return wrap

#--------------------------------
# helpers
#

def userLoggedIn():
    return 'user' in session

def userIsAdmin():
    return 'user' in session and session['user'].isAdmin

def checkAdmin(clientOpt):
    b = config.getboolean('client', clientOpt)
    return userIsAdmin() if b else True
    
def validateParams(params, rules):
    for param, rule in rules.items():
        if param in params:
            if not isinstance(params[param], rule[0]):
                if params[param] is not None or (len(rule) > 1 and rule[1]):
                    raise ValidationError('{} is not of type {}'.format(param, str(rule[0])))
        else:
            if len(rule) == 1 or rule[1]:
                raise ValidationError('{} is required'.format(param))
    
#================================================================
# socket events
# These events represent the client-side API
#

#-------------------------------
# special
#
    
@socket.on_error_default  # handles all namespaces without an explicit error handler
def _socket_default_error_handler(e):
    _logger.exception(e)
    return error('An internal error has ocurred!')
    
@socket.on('connect')
def _socket_connect():
    global _consoleSessionId
    _logger.info('Connection opened from ' + request.remote_addr)
    emit('options', _buildOptions())
    emit('units', _buildUnits())
    drinkOrder = dispenser.drinkOrder
    if drinkOrder:
        drinkOrder = drinkOrder.toDict(drink = True, glass = True)
    emit('dispenser_state', {'state': dispenser.state, 'drinkOrder': drinkOrder})
    emit('dispenser_glass', dispenser.glass)
    emit('dispenser_parentalCode', True if dispenser.getParentalCode() else False)
    emit('pumps', [pump.toDict(ingredient = True) for pump in Pump.getAllPumps()])
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

#-------------------------------
# core
#
    
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

#-------------------------------
# audio
#
        
@socket.on('audio_setVolume')
def _socket_audio_setVolume(volume):
    audio.setVolume(float(volume))
    return success()

#-------------------------------
# dispenser
#

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
        
#-------------------------------
# wifi
#
        
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

#-------------------------------
# glass
#

@socket.on('glass_getAll')
def _socket_glass_getAll():
    return success(glasses = [g.toDict() for g in Glass.select()])

@socket.on('glass_getOne')
def _socket_glass_getOne(id):
    glass = Glass.get_or_none(Glass.id == id)
    if not glass:
        return error('Glass not found!')
    return success(glass = glass.toDict(drinks = True))

@socket.on('glass_save')
@validate({
    'id': [int, False],
    'type': [str, False],
    'size': [int, False],
    'units': [str, False],
    'description': [str, False],
    
})
def _socket_glass_save(params):
    try:
        if 'id' in params:
            glass = Glass.get_or_none(Glass.id == params['id'])
            if not glass:
                return error('Glass not found!')
        else:
            glass = Glass()

        if 'type' in params:
            glass.type = params['type']
        if 'size' in params:
            glass.size = params['size']
        if 'units' in params:
            glass.units = params['units']
        if 'description' in params:
            glass.description = params['description']
            
        glass.save()
        socket.emit('glass_changed', glass.toDict(drinks = True))
        return success()
        
    except ModelError as e:
        return error(e)

@socket.on('glass_delete')
def _socket_glass_delete(id):
    try:
        glass = Glass.get_or_none(Glass.id == id)
        if not glass:
            return error('Glass not found!')
        glass.delete_instance()
        socket.emit('glass_deleted', glass.toDict())
        return success()
    except ModelError as e:
        return error(e)
         
#-------------------------------
# ingredient
#

@socket.on('ingredient_getAll')
def _socket_ingredient_getAll():
    return success(ingredients = [i.toDict() for i in Ingredient.select()])

@socket.on('ingredient_getOne')
def _socket_ingredient_getOne(id):
    ingredient = Ingredient.get_or_none(Ingredient.id == id)
    if not ingredient:
        return error('Ingredient not found!')
    return success(ingredient = ingredient.toDict(drinks = True))
    
@socket.on('ingredient_save')
@validate({
    'id': [int, False],
    'name': [str, False],
    'isAlcoholic': [bool, False],
    'timesDispensed': [int, False],
    'amountDispensed': [(float, int), False],
    'lastContainerAmount': [(float, int), False],
    'lastAmount': [(float, int), False],
    'lastUnits': [str, False],
})
def _socket_ingredient_save(params):
    try:
        if 'id' in params:
            ingredient = Ingredient.get_or_none(Ingredient.id == params['id'])
            if not ingredient:
                return error('Ingredient not found!')
        else:
            ingredient = Ingredient()

        if 'name' in params:
            ingredient.name = params['ingredient']
        if 'isAlcoholic' in params:
            ingredient.isAlcoholic = params['isAlcoholic']
        if 'timesDispensed' in params:
            ingredient.timesDispensed = params['timesDispensed']
        if 'amountDispensed' in params:
            ingredient.amountDispensed = params['amountDispensed']
        if 'lastContainerAmount' in params:
            ingredient.lastContainerAmount = params['lastContainerAmount']
        if 'lastAmount' in params:
            ingredient.lastAmount = params['lastAmount']
        if 'lastUnits' in params:
            ingredient.lastUnits = params['lastUnits']
            
        ingredient.save()
        socket.emit('ingredient_changed', ingredient.toDict(drinks = True))
        return success()
        
    except ModelError as e:
        return error(e)

@socket.on('ingredient_delete')
def _socket_ingredient_delete(id):
    try:
        ingredient = Ingredient.get_or_none(Ingredient.id == id)
        if not ingredient:
            return error('Ingredient not found!')
        ingredient.delete_instance()
        socket.emit('ingredient_deleted', ingredient.toDict())
        return success()
    except ModelError as e:
        return error(e)

#-------------------------------
# drink
#

@socket.on('drink_getAll')
def _socket_drink_getAll():
    return success(drinks = [d.toDict(glass = True, ingredients = True) for d in Drink.select()])
    
@socket.on('drink_getOne')
def _socket_drink_getOne(id):
    drink = Drink.get_or_none(Drink.id == id)
    if not drink:
        return error('Drink not found!')
    return success(drink = drink.toDict(glass = True, ingredients = True))
    
@socket.on('drink_save')
@validate({
    'id': [int, False],
    'primaryName': [str, False],
    'secondaryName': [str, False],
    'glass_id': [int, False],
    'instructions': [str, False],
    'isFavorite': [bool, False],
    'timesDispensed': [int, False],
    'ingredients': [list, False],
})
@db.atomic()
def _socket_drink_save(params):
    try:
        if 'id' in params:
            drink = Drink.get_or_none(Drink.id == params['id'])
            if not drink:
                return error('Drink not found!')
        else:
            drink = Drink()

        if 'glass_id' in params:
            glass = Glass.get_or_none(Glass.id == params['glass_id'])
            if not glass:
                return error('Glass not found!')
            drink.glass = glass
            
        if 'primaryName' in params:
            drink.primaryName = params['primaryName']
        if 'secondaryName' in params:
            drink.secondaryName = params['secondaryName']
        if 'instructions' in params:
            drink.instructions = params['instructions']
        if 'isFavorite' in params:
            drink.isFavorite = params['isFavorite']
        if 'timesDispensed' in params:
            drink.timesDispensed = params['timesDispensed']
            
        if 'ingredients' in params:
            if drink.get_id() is None:
                drink.save()
            drink.setIngredients(params['ingredients'])
        
        drink.save()
        socket.emit('drink_changed', drink.toDict(glass = True, ingredients = True))
        return success()
        
    except ModelError as e:
        return error(e)

@socket.on('drink_delete')
def _socket_drink_delete(id):
    try:
        drink = Drink.get_or_none(Drink.id == id)
        if not drink:
            return error('Drink not found!')
        drink.delete_instance()
        socket.emit('drink_deleted', drink.toDict())
        return success()
    except ModelError as e:
        return error(e)

#-------------------------------
# pump
#
 
@socket.on('pump_getAll')
def _socket_pump_getAll():
    return success(items = [p.toDict(ingredient = True) for p in Pump.select()])
 
@socket.on('pump_load')
@requireDispenserState(dispenser.ST_SETUP)
@validate({
    'pump_id': [int, True],
    'ingredient_id': [int, True],
    'containerAmount': [(float, int), True],
    'units': [str, True],
    'amount': [(float, int), True]
})
def _socket_pump_load(params):
    try:
        pump = Pump.get_or_none(Pump.id == params['pump_id'])
        if not pump:
            return error('Pump not found!')
        if not (pump.isUnused() or pump.isReady() or pump.isEmpty()):
            return error('Invalid pump state!')
            
        ingredient = Ingredient.get_or_none(Ingredient.id == params['ingredient_id'])
        if not ingredient:
            return error('Ingredient not found!')
        
        pump.load(ingredient, params['containerAmount'], params['units'], params['amount'])
        socket.emit('pump_changed', pump.toDict(ingredient = True))
        return success()
        
    except ModelError as e:
        return error(e)
    

@socket.on('pump_unload')
@requireDispenserState(dispenser.ST_SETUP)
def _socket_pump_unload(id):
    try:
        pump = Pump.get_or_none(Pump.id == id)
        if not pump:
            return error('Pump not found!')
        if not pump.isLoaded():
            return error('Invalid pump state!')
            
        pump.unload()
        socket.emit('pump_changed', pump.toDict(ingredient = True))
        return success()
        
    except ModelError as e:
        return error(e)
    
@socket.on('pump_prime')
@requireDispenserState(dispenser.ST_SETUP)
def _socket_pump_prime(id):
    try:
        pump = Pump.get_or_none(Pump.id == id)
        if not pump:
            return error('Pump not found!')
        if not pump.isLoaded():
            return error('Invalid pump state!')
            
        pump.prime()
        return success()
        
    except ModelError as e:
        return error(e)

@socket.on('pump_drain')
@requireDispenserState(dispenser.ST_SETUP)
def _socket_pump_drain(id):
    try:
        pump = Pump.get_or_none(Pump.id == id)
        if not pump:
            return error('Pump not found!')
        if not (pump.isReady() or pump.isEmpty() or pump.isUnused() or pump.isDirty()):
            return error('Invalid pump state!')
            
        pump.drain()
        return success()

    except ModelError as e:
        return error(e)
        
@socket.on('pump_clean')
@requireDispenserState(dispenser.ST_SETUP)
def _socket_pump_clean(id):
    try:
        pump = Pump.get_or_none(Pump.id == id)
        if not pump:
            return error('Pump not found!')
        if not (pump.isEmpty() or pump.isUnused() or pump.isDirty()):
            return error('Invalid pump state!')
            
        pump.clean()
        return success()

    except ModelError as e:
        return error(e)
        
@socket.on('pump_start')
@requireDispenserState(dispenser.ST_SETUP)
def _socket_pump_start(id):
    try:
        pump = Pump.get_or_none(Pump.id == id)
        if not pump:
            return error('Pump not found!')
            
        pump.start(0, forward = True)
        return success()

    except ModelError as e:
        return error(e)
    
@socket.on('pump_stop')
@requireDispenserState(dispenser.ST_SETUP)
def _socket_pump_stop(id):
    try:
        pump = Pump.get_or_none(Pump.id == id)
        if not pump:
            return error('Pump not found!')
            
        pump.stop()
        return success()

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
    socket.emit('clientOptions', _buildOptions())
    socket.emit('units', _buildUnits())
    
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

#@bus.on('model/glass/saved')
#def _bus_modelGlassSaved(g):
#    socket.emit('glassSaved', g.toDict())

#@bus.on('model/glass/deleted')
#def _bus_modelGlassDeleted(g):
#    socket.emit('glassDeleted', g.toDict())

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
    
@bus.on('model/pump/changed')
def _bus_model_pump_changed(p):
    socket.emit('pump_changed', p.toDict(ingredient = True))
    

    
def _buildOptions():
    opts = dict(config.items('client'))
    for k, v in opts.items():
        if _booleanPattern.match(v):
            opts[k] = config.getboolean('client', k)
        elif _intPattern.match(v):
            opts[k] = config.getint('client', k)
        elif _floatPattern.match(v):
            opts[k] = config.getfloat('client', k)
    return opts
            
def _buildUnits():
    u = {
        'default': units.default,
        'order': units.order,
        'conversions': units.conversions,
    }
    return u
    