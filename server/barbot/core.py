
import logging, os, time, subprocess

from .bus import bus
from .config import config
from .db import db
from . import serial
from . import utils
from . import dispenser
from .models.Drink import Drink
from .models.DrinkOrder import DrinkOrder
from .models.Pump import Pump, anyPumpsRunning


_logger = logging.getLogger('Core')
_enterPumpSetup = False
_suppressMenuRebuild = False


class CoreError(Exception):
    pass

@bus.on('server/start')
def _bus_serverStart():
    _rebuildMenu()

@bus.on('socket/consoleConnect')
def _bus_consoleConnect():
    try:
        serial.write('RO', timeout = 1)  # power on, turn off lights
    except serial.SerialError as e:
        _logger.error(e)
            
def restartX():
    cmd = config.get('core', 'restartXCommand').split(' ')
    out = subprocess.run(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
    if out.returncode != 0:
        _logger.error('Error trying to restart X: {}'.format(out.stdout))
        
def restart():
    if Pump.setup or Pump.flushing or anyPumpsRunning():
        raise CoreError('Unable to restart while in pump setup or any pumps are running!')

    bus.emit('lights/play', 'restart')
    bus.emit('audio/play', 'restart', console = True)
    time.sleep(2)
    
    cmd = config.get('core', 'restartCommand').split(' ')
    out = subprocess.run(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
    if out.returncode != 0:
        _logger.error('Error trying to restart: {}'.format(out.stdout))
        
def shutdown():
    if Pump.setup or Pump.flushing or Pump.anyPumpsRunning:
        raise CoreError('Unable to restart while in pump setup or any pumps are running!')
        
    bus.emit('lights/play', 'shutdown')
    bus.emit('audio/play', 'shutdown', console = True)
    try:
        serial.write('RT{}'.format(config.get('core', 'shutdownTimer')))
    except serial.SerialError as e:
        _logger.error(e)
    time.sleep(2)
    
    cmd = config.get('core', 'shutdownCommand').split(' ')
    out = subprocess.run(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
    if out.returncode != 0:
        _logger.error('Error trying to shutdown: {}'.format(out.stdout))
    
def startPumpSetup():
    global _pumpSetup
    dispenser.startPause()
    _pumpSetup = True
    
def stopPumpSetup():
    global _pumpSetup
    _pumpSetup = False
    Pump.stopSetup()
    dispenser.stopPause()
    _rebuildMenu()

@bus.on('dispenser/state')
def _bus_dispenserState(state, drinkOrder):
    if state == dispenser.ST_PAUSE and _pumpSetup:
        Pump.startSetup()

def setParentalCode(code):
    if not code:
        try:
            os.remove(config.getpath('core', 'parentalCodeFile'))
        except IOError:
            pass
    else:
        open(config.getpath('core', 'parentalCodeFile'), 'w').write(code)
    bus.emit('core/parentalCode', True if code else False)

def getParentalCode():
    try:
        return open(config.getpath('core', 'parentalCodeFile')).read().rstrip()
    except IOError:
        return False

def submitDrinkOrder(item):
    d = Drink.get(Drink.id == item['drinkId'])
    if d.isAlcoholic:
        code = getParentalCode()
        if code:
            if not 'parentalCode' in item:
                raise CoreError('Parental code required!')
            if item['parentalCode'] != code:
                raise CoreError('Invalid parental code!')
    o = DrinkOrder.submitFromDict(item)
    bus.emit('core/drinkOrderSubmitted', o)
    bus.emit('audio/play', 'drinkOrderSubmitted', sessionId = o.sessionId)

def cancelDrinkOrder(id):
    o = DrinkOrder.cancelById(id)
    bus.emit('core/drinkOrderCancelled', o)
    bus.emit('audio/play', 'drinkOrderCancelled', sessionId = o.sessionId)
        
def toggleDrinkOrderHold(id):
    o = DrinkOrder.toggleHoldById(id)
    bus.emit('core/drinkOrderHoldToggled', o)
    bus.emit('audio/play', 'drinkOrderOnHold' if o.userHold else 'drinkOrderOffHold', sessionId = o.sessionId)
    
@bus.on('model/drink/saved')
def _bus_drinkSaved(drink):
    if not _suppressMenuRebuild:
        _rebuildMenu()

@bus.on('model/drink/deleted')
def _bus_drinkDeleted(drink):
    _rebuildMenu()

@db.atomic()
def _rebuildMenu():
    global _suppressMenuRebuild
    _logger.info('Rebuilding drinks menu')
    _suppressMenuRebuild = True
    menuUpdated = False
    ingredients = Pump.getReadyIngredients()
    menuDrinks = Drink.getMenuDrinks()

    # trivial case
    if not ingredients:
        for drink in menuDrinks:
            drink.isOnMenu = False
            drink.save()
            menuUpdated = True
        
    else:
        for drink in Drink.getDrinksWithIngredients(ingredients):
            # remove this drink from the existing menu drinks
            menuDrinks = [d for d in menuDrinks if d.id != drink.id]
            
            onMenu = True
            # check for all the drink's ingredients
            for di in drink.ingredients:
                pump = Pump.getPumpWithIngredientId(di.ingredient_id)
                if not pump or pump.state == Pump.EMPTY or utils.toML(pump.amount, pump.units) < utils.toML(di.amount, di.units):
                    onMenu = False
                    break
            if onMenu != drink.isOnMenu:
                drink.isOnMenu = onMenu
                drink.save()
                menuUpdated = True
    
        # any drinks in the original list are no longer on the menu
        for drink in menuDrinks:
            drink.isOnMenu = False
            drink.save()
            menuUpdated = True
            
    bus.emit('barbot/drinksMenuUpdated')
        
    _updateDrinkOrders()
    _suppressMenuRebuild = False

@db.atomic()
def _updateDrinkOrders():
    _logger.info('Updating drink orders')
    readyPumps = Pump.getReadyPumps()
    for o in DrinkOrder.getWaiting():
        if o.drink.isOnMenu == o.ingredientHold:
            o.ingredientHold = not o.drink.isOnMenu
            o.save()
            
