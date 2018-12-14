
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
from . import lights
from . import alerts
from . import settings

from .models.Drink import Drink
from .models.DrinkIngredient import DrinkIngredient
from .models.DrinkOrder import DrinkOrder
from .models.Glass import Glass
from .models.Ingredient import Ingredient
from .models.IngredientAlternative import IngredientAlternative
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

def socketEmit(*args, **kwargs):
    if not socket.server: return
    socket.emit(*args, **kwargs)

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
    
def requireDispenserState(*states):
    def wrap(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if dispenser.state in states:
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
    b = settings.getboolean(clientOpt)
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
    _logger.info('Connection opened from {}'.format(request.remote_addr))
    emit('settings', settings.export())
    emit('units', units.export())
    drinkOrder = dispenser.drinkOrder
    if drinkOrder:
        drinkOrder = drinkOrder.toDict(drink = True, glass = True)
    emit('dispenser_state', {'state': dispenser.state, 'drinkOrder': drinkOrder})
    emit('dispenser_glass', dispenser.glass)
    emit('dispenser_hold', dispenser.hold)
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
    _logger.info('Connection closed from {}'.format(request.remote_addr))
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

@socket.on('core_statistics')
def _socket_core_statistics():
    _logger.debug('recv core_statistics')
    stats = {
        'drinks': Drink.select().count(),
        'ingredients': Ingredient.select().count(),
        'glasses': Glass.select().count(),
        'menuDrinks': Drink.getMenuDrinksCount(),
        'drinksServed': dispenser.drinksServed,
    }
    return success(stats)
    
@socket.on('core_restartX')
def _socket_core_restartX():
    _logger.debug('recv core_restartX')
    if not checkAdmin('restartXRequiresAdmin'):
        return error('Permission denied!')
    _logger.info('Client requested restart X')
    try:
        core.restartX()
        return success()
    except core.CoreError as e:
        return error(e)

@socket.on('core_restart')
def _socket_core_restart():
    _logger.debug('recv core_restart')
    if not checkAdmin('restartRequiresAdmin'):
        return error('Permission denied!')
    _logger.info('Client requested restart')
    try:
        core.restart()
        return success()
    except core.CoreError as e:
        return error(e)

@socket.on('core_shutdown')
def _socket_core_shutdown():
    _logger.debug('recv core_shutdown')
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
    _logger.debug('recv audio_setVolume')
    audio.setVolume(float(volume))
    return success()

#-------------------------------
# dispenser
#

@socket.on('dispenser_startSetup')
def _socket_dispenser_startSetup():
    _logger.debug('recv dispenser_startSetup')
    if not checkAdmin('dispenserSetupRequiresAdmin'):
        return error('Permission denied!')
    dispenser.startSetup()
    return success()
    
@socket.on('dispenser_stopSetup')
def _socket_dispenser_stopSetup():
    _logger.debug('recv dispenser_stopSetup')
    dispenser.stopSetup()
    return success()
        
@socket.on('dispenser_startHold')
def _socket_dispenser_startHold():
    _logger.debug('recv dispenser_startHold')
    try:
        dispenser.startHold()
        return success()
    except dispenser.DispenserError as e:
        return error(e)

@socket.on('dispenser_stopHold')
def _socket_dispenser_stopHold():
    _logger.debug('recv dispenser_stopHold')
    try:
        dispenser.stopHold()
        return success()
    except dispenser.DispenserError as e:
        return error(e)

@socket.on('dispenser_startManual')
def _socket_dispenser_startManul():
    _logger.debug('recv dispenser_startManual')
    try:
        dispenser.startManual()
        return success()
    except dispenser.DispenserError as e:
        return error(e)

@socket.on('dispenser_stopManual')
def _socket_dispenser_stopManual():
    _logger.debug('recv dispenser_stopManual')
    try:
        dispenser.stopManual()
        return success()
    except dispenser.DispenserError as e:
        return error(e)
        
@socket.on('dispenser_setControl')
def _socket_dispenser_setControl(ctl):
    _logger.debug('recv dispenser_setControl')
    dispenser.setControl(ctl)
    return success()
    
@socket.on('dispenser_startPump')
@validate({
    'id': [int, True],
    'parentalCode': [str, False]
})
def _socket_dispenser_startPump(params):
    _logger.debug('recv dispenser_startPump')
    try:
        dispenser.startPump(params['id'], params['parentalCode'] if 'parentalCode' in params else False)
        return success()
    except dispenser.DispenserError as e:
        return error(e)
    
@socket.on('dispenser_stopPump')
def _socket_dispenser_stopPump(id):
    _logger.debug('recv dispenser_stopPump')
    try:
        dispenser.stopPump(id)
        return success()
    except dispenser.DispenserError as e:
        return error(e)

#-------------------------------
# wifi
#
        
@socket.on('wifi_getNetworks')
def _socket_wifi_getNetworks():
    _logger.debug('recv wifi_getNetworks')
    return success(networks = wifi.getNetworks())
    
@socket.on('wifi_connectToNetwork')
def _socket_wifi_connectToNetwork(params):
    _logger.debug('recv wifi_connectToNetwork')
    wifi.connectToNetwork(params)
    return success()
    
@socket.on('wifi_disconnectFromNetwork')
def _socket_wifi_disconnectFromNetwork(ssid):
    _logger.debug('recv wifi_disconnectFromNetwork')
    wifi.disconnectFromNetwork(ssid)
    return success()
    
@socket.on('wifi_forgetNetwork')
def _socket_wifi_forgetNetwork(ssid):
    _logger.debug('recv wifi_forgetNetwork')
    wifi.forgetNetwork(ssid)
    return success()

#-------------------------------
# glass
#

@socket.on('glass_getAll')
def _socket_glass_getAll():
    _logger.debug('recv glass_getAll')
    return success(glasses = [g.toDict() for g in Glass.select()])

@socket.on('glass_getOne')
def _socket_glass_getOne(id):
    _logger.debug('recv glass_getOne')
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
    _logger.debug('recv glass_save')
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
        return success()
        
    except ModelError as e:
        return error(e)

@socket.on('glass_delete')
def _socket_glass_delete(id):
    _logger.debug('recv glass_delete')
    try:
        glass = Glass.get_or_none(Glass.id == id)
        if not glass:
            return error('Glass not found!')
        glass.delete_instance()
        return success()
    except ModelError as e:
        return error(e)
         
#-------------------------------
# ingredient
#

@socket.on('ingredient_getAll')
def _socket_ingredient_getAll():
    _logger.debug('recv ingredient_getAll')
    return success(ingredients = [i.toDict(alternatives = True) for i in Ingredient.select()])

@socket.on('ingredient_getOne')
def _socket_ingredient_getOne(id):
    _logger.debug('recv ingredient_getOne')
    ingredient = Ingredient.get_or_none(Ingredient.id == id)
    if not ingredient:
        return error('Ingredient not found!')
    return success(ingredient = ingredient.toDict(drinks = True, alternatives = True))
    
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
    'alternatives': [list, False],
})
def _socket_ingredient_save(params):
    _logger.debug('recv ingredient_save')
    try:
        if 'id' in params:
            ingredient = Ingredient.get_or_none(Ingredient.id == params['id'])
            if not ingredient:
                return error('Ingredient not found!')
        else:
            ingredient = Ingredient()

        if 'name' in params:
            ingredient.name = params['name']
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
         
        if 'alternatives' in params:

            ingredientAlternatives = []
            for alt in params['alternatives']:
                try:
                    validateParams(alt, {
                        'id': [int, True],
                    })
                except ValidationError as e:
                    return error(e)
                    
                alternative = Ingredient.get_or_none(Ingredient.id == alt['id'])
                if not alternative:
                    return error('Ingredient {} not found!'.format(alt['alternative_id']))
                    
                ingredientAlternative = IngredientAlternative()
                ingredientAlternative.ingredient = ingredient
                ingredientAlternative.alternative = alternative
                ingredientAlternative.priority = len(ingredientAlternatives)
                ingredientAlternatives.append(ingredientAlternative)

            ingredient.setAlternatives(ingredientAlternatives)
            
        Drink.rebuildMenu()
        return success()
        
    except ModelError as e:
        return error(e)

@socket.on('ingredient_delete')
def _socket_ingredient_delete(id):
    _logger.debug('recv ingredient_delete')
    try:
        ingredient = Ingredient.get_or_none(Ingredient.id == id)
        if not ingredient:
            return error('Ingredient not found!')
        ingredient.delete_instance()
        return success()
    except ModelError as e:
        return error(e)

#-------------------------------
# drink
#

@socket.on('drink_getAll')
def _socket_drink_getAll():
    _logger.debug('recv drink_getAll')
    return success(drinks = [d.toDict(glass = True, ingredients = True) for d in Drink.select()])

@socket.on('drink_getMenu')
def _socket_drink_getMenu():
    _logger.debug('recv drink_getMenu')
    return success(drinks = [d.toDict() for d in Drink.getMenuDrinks()])
    
@socket.on('drink_rebuildMenu')
def _socket_drink_rebuildMenu():
    _logger.debug('recv drink_rebuildMenu')
    Drink.rebuildMenu()
    return success()
    
@socket.on('drink_getOne')
def _socket_drink_getOne(id):
    _logger.debug('recv drink_getOne')
    drink = Drink.get_or_none(Drink.id == id)
    if not drink:
        return error('Drink not found!')
    return success(drink = drink.toDict(glass = True, ingredients = True, ingredientAlternatives = True))
    
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
    _logger.debug('recv drink_save')
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

            drinkIngredients = []
            for i in params['ingredients']:
                try:
                    validateParams(i, {
                        'ingredient_id': [int, True],
                        'step': [int, True],
                        'amount': [(float, int), True],
                        'units': [str, True],
                    })
                except ValidationError as e:
                    return error(e)
                    
                ingredient = Ingredient.get_or_none(Ingredient.id == i['ingredient_id'])
                if not ingredient:
                    return error('Ingredient {} not found!'.format(i['ingredient_id']))
                    
                drinkIngredient = DrinkIngredient()
                drinkIngredient.drink = drink
                drinkIngredient.ingredient = ingredient
                drinkIngredient.ingredient_id = ingredient.id
                drinkIngredient.amount = i['amount']
                drinkIngredient.units = i['units']
                drinkIngredient.step = i['step']
                drinkIngredients.append(drinkIngredient)
                
            drink.setIngredients(drinkIngredients)
        
        drink.save()
        Drink.rebuildMenu()
        return success()
        
    except ModelError as e:
        return error(e)

@socket.on('drink_delete')
def _socket_drink_delete(id):
    _logger.debug('recv drink_delete')
    try:
        drink = Drink.get_or_none(Drink.id == id)
        if not drink:
            return error('Drink not found!')
        drink.delete_instance()
        Drink.rebuildMenu()
        return success()
    except ModelError as e:
        return error(e)

        
#-------------------------------
# drinkOrder
#
 
@socket.on('drinkOrder_getWaiting')
def _socket_drinkOrder_getWaiting():
    _logger.debug('recv drinkOrder_getWaiting')
    return success(drinkOrders = [do.toDict(drink = True) for do in DrinkOrder.getWaiting()])

@socket.on('drinkOrder_getOne')
def _socket_drinkOrder_getOne(id):
    _logger.debug('recv drinkOrder_getOne')
    drinkOrder = DrinkOrder.get_or_none(DrinkOrder.id == id)
    if not drinkOrder:
        return error('Drink order not found!')
    return success(drinkOrder = drinkOrder.toDict(drink = True))
    
@socket.on('drinkOrder_submit')
@validate({
    'drink_id': [int, True],
    'name': [str, False],
    'userHold': [bool, False],
    'parentalCode': [str, False],
})
def _socket_drinkOrder_submit(params):
    _logger.debug('recv drinkOrder_submit')
    try:
        drink = Drink.get_or_none(Drink.id == params['drink_id'])
        if not drink:
            return error('Drink not found!')
        if drink.isAlcoholic:
            code = settings.get('parentalCode')
            if code:
                if 'parentalCode' not in params:
                    return error('Parental code required!')
                if params['parentalCode'] != code:
                    return error('Invalid parental code!')

        drinkOrder = DrinkOrder()
        drinkOrder.drink = drink
        drinkOrder.sessionId = request.sid
        if 'name' in params:
            drinkOrder.name = params['name']
        if 'userHold' in params:
            drinkOrder.userHold = params['userHold']
        drinkOrder.save()
        bus.emit('audio/play', 'drinkOrderSubmitted', sessionId = drinkOrder.sessionId)
        return success()
        
    except ModelError as e:
        return error(e)
        
@socket.on('drinkOrder_cancel')
def _socket_drinkOrder_cancel(id):
    _logger.debug('recv drinkOrder_cancel')
    try:
        drinkOrder = DrinkOrder.get_or_none(DrinkOrder.id == id, DrinkOrder.startedDate.is_null())
        if not drinkOrder:
            return error('Drink order not found!')
        drinkOrder.delete_instance()
        bus.emit('audio/play', 'drinkOrderCancelled', sessionId = drinkOrder.sessionId)
        return success()
        
    except ModelExist as e:
        return error(e)
        
@socket.on('drinkOrder_toggleHold')
def _socket_drinkOrder_toggleHold(id):
    _logger.debug('recv drinkOrder_toggleHold')
    try:
        drinkOrder = DrinkOrder.get_or_none(DrinkOrder.id == id, DrinkOrder.startedDate.is_null())
        if not drinkOrder:
            return error('Drink order not found!')
        drinkOrder.userHold = not o.userHold
        drinkOrder.save()
        bus.emit('audio/play', 'drinkOrderOnHold' if drinkOrder.userHold else 'drinkOrderOffHold', sessionId = drinkOrder.sessionId)
        return success()
        
    except ModelExist as e:
        return error(e)
 
#-------------------------------
# pump
#
 
@socket.on('pump_getAll')
def _socket_pump_getAll():
    _logger.debug('recv pump_getAll')
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
    _logger.debug('recv pump_load')
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
        return success()
        
    except ModelError as e:
        return error(e)
    

@socket.on('pump_unload')
@requireDispenserState(dispenser.ST_SETUP)
def _socket_pump_unload(id):
    _logger.debug('recv pump_unload')
    try:
        pump = Pump.get_or_none(Pump.id == id)
        if not pump:
            return error('Pump not found!')
        if not pump.isLoaded():
            return error('Invalid pump state!')
            
        pump.unload()
        return success()
        
    except ModelError as e:
        return error(e)
    
@socket.on('pump_prime')
@requireDispenserState(dispenser.ST_SETUP)
def _socket_pump_prime(id):
    _logger.debug('recv pump_prime')
    try:
        pump = Pump.get_or_none(Pump.id == id)
        if not pump:
            return error('Pump not found!')
        if not pump.isLoaded():
            return error('Invalid pump state!')
            
        bus.emit('lights/play', 'setupDispense')
        pump.prime()
        return success()
        
    except ModelError as e:
        return error(e)

@socket.on('pump_drain')
@requireDispenserState(dispenser.ST_SETUP)
def _socket_pump_drain(id):
    _logger.debug('recv pump_drain')
    try:
        pump = Pump.get_or_none(Pump.id == id)
        if not pump:
            return error('Pump not found!')
        if not (pump.isReady() or pump.isEmpty() or pump.isUnused() or pump.isDirty()):
            return error('Invalid pump state!')
            
        bus.emit('lights/play', 'setupDispense')
        pump.drain()
        return success()

    except ModelError as e:
        return error(e)
        
@socket.on('pump_clean')
@requireDispenserState(dispenser.ST_SETUP)
def _socket_pump_clean(id):
    _logger.debug('recv pump_clean')
    try:
        pump = Pump.get_or_none(Pump.id == id)
        if not pump:
            return error('Pump not found!')
        if not (pump.isEmpty() or pump.isUnused() or pump.isDirty()):
            return error('Invalid pump state!')
            
        bus.emit('lights/play', 'setupDispense')
        pump.clean()
        return success()

    except ModelError as e:
        return error(e)
        

#-------------------------------
# settings
#

@socket.on('settings_set')
@validate({
    'key': [str, True],
    'value': [(str, bool, int, float), True],
})
def socket_settings_set(params):
    _logger.debug('recv settings_set')
    try:
        settings.set(params['key'], params['value'])
        return success()
    except ValueError as e:
        return error(e)
        
#-------------------------------
# alerts
#     
    
@socket.on('alerts_clear')
def socket_alerts_clear():
    _logger.debug('recv alerts_clear')
    alerts.clear()
    return success()
    
    
    
#================================================================
# bus events
#
    
#-------------------------------
# misc
#
    
@bus.on('config/loaded')
def _but_config_loaded():
    socketEmit('units', units.export())
    
@bus.on('settings/loaded')
@bus.on('settings/changed')
def _but_settings_loaded():
    socketEmit('settings', settings.export())
    
@bus.on('serial/event')
def _bus_serial_event(e):
    if _consoleSessionId:
        m = _shutdownEventPattern.match(e)
        if m:
            _logger.debug('Got shutdown request')
            socketEmit('shutdownRequest', room = _consoleSessionId)
    
#-------------------------------
# alert
#
    
@bus.on('alerts/add')
@bus.on('alerts/clear')
def _bus_alerts():
    try:
        socketEmit('alerts_changed', alerts.getAll())
    except:
        pass
    
#-------------------------------
# dispenser
#

@bus.on('dispenser/state')
def _bus_dispenser_state(state, drinkOrder):
    if drinkOrder:
        drinkOrder = drinkOrder.toDict(drink = True, glass = True)
    socketEmit('dispenser_state', {'state': state, 'drinkOrder': drinkOrder})
    
@bus.on('dispenser/glass')
def _bus_dispenser_glass(ready):
    socketEmit('dispenser_glass', ready)

@bus.on('dispenser/hold')
def _bus_dispenser_hold(hold):
    socketEmit('dispenser_hold', hold)

#-------------------------------
# wifi
#

@bus.on('wifi/state')
def _bus_wifi_state(state):
    socketEmit('wifi_state', state)
    
#-------------------------------
# audio
#
    
@bus.on('audio/playFile')
def _bus_audio_playFile(file, console, sessionId, broadcast):
    if broadcast:
        _logger.debug('Play {} everywhere'.format(file))
        socketEmit('audio_playFile', file)
    else:
        if sessionId:
            _logger.debug('Play {} on client {}'.format(file, sessionId))
            socketEmit('audio_playFile', file, room = sessionId)
        elif console and _consoleSessionId:
            _logger.debug('Play {} on console'.format(file))
            socketEmit('audio_playFile', file, room = _consoleSessionId)

@bus.on('audio/volume')
def _bus_audio_volume(volume):
    if _consoleSessionId:
        socketEmit('audio_volume', volume, room = _consoleSessionId)
        
#-------------------------------
# glass
#

@bus.on('model/glass/saved')
def _bus_model_glass_saved(g):
    _logger.debug('emit glass_changed')
    socketEmit('glass_changed', g.toDict(drinks = True))

@bus.on('model/glass/deleted')
def _bus_model_glass_deleted(g):
    _logger.debug('emit glass_delete')
    socketEmit('glass_deleted', g.toDict())

#-------------------------------
# ingredient
#
            
@bus.on('model/ingredient/saved')
def _bus_model_ingredient_saved(i):
    _logger.debug('emit ingredient_changed')
    socketEmit('ingredient_changed', i.toDict(drinks = True, alternatives = True))

@bus.on('model/ingredient/deleted')
def _bus_model_ingredient_deleted(i):
    _logger.debug('emit ingredient_deleted')
    socketEmit('ingredient_deleted', i.toDict())
                 
#-------------------------------
# drink
#

@bus.on('model/drink/saved')
def _bus_model_drink_saved(d):
    _logger.debug('emit drink_changed')
    socketEmit('drink_changed', d.toDict(glass = True, ingredients = True))

@bus.on('model/drink/deleted')
def _bus_model_drink_deleted(d):
    _logger.debug('emit drink_deleted')
    socketEmit('drink_deleted', d.toDict())
    
#-------------------------------
# drinkOrder
#

@bus.on('model/drinkOrder/saved')
def _bus_model_drinkOrder_saved(o):
    _logger.debug('emit drinkOrder_changed')
    socketEmit('drinkOrder_changed', o.toDict(drink = True))

@bus.on('model/drinkOrder/deleted')
def _bus_model_drinkOrder_deleted(o):
    _logger.debug('emit drinkOrder_deleted')
    socketEmit('drinkOrder_deleted', o.toDict())
         
#-------------------------------
# pump
#
    
@bus.on('model/pump/saved')
def _bus_model_pump_saved(p):
    _logger.debug('emit pump_changed')
    socketEmit('pump_changed', p.toDict(ingredient = True))
    

