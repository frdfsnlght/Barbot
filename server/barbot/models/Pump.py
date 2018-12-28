
import logging, time, threading, re
from peewee import *
from threading import Lock, Timer

from ..db import db, BarbotModel, ModelError, addModel
from ..config import config
from ..bus import bus
from .. import units
from .. import serial
from .Ingredient import Ingredient


_pumpRunEventPattern = re.compile(r"(?i)PR(\d+)")
_pumpStopEventPattern = re.compile(r"(?i)PS(\d+),(-?\d+)")

_logger = logging.getLogger('Models.Pump')

_pumpExtras = {}

@bus.on('server/start')
def _bus_serverStart():
    _bus_configLoaded()
    pumps = Pump.select()
    if len(pumps) != config.getint('pumps', 'count'):
        _logger.warning('Database pump count doesn\'t match configuration count!')
        Pump.delete().execute()
        for i in range(0, config.getint('pumps', 'count')):
            p = Pump()
            p.id = i + 1
            p.save(force_insert = True)
        _logger.info('Initialized pumps')

@bus.on('config/loaded')
def _bus_configLoaded():
    try:
        serial.write('PS{}'.format(config.getint('pumps', 'speed')), timeout = 1)
        serial.write('PA{}'.format(config.getint('pumps', 'acceleration')), timeout = 1)
    except serial.SerialError as e:
        _logger.error(e)
        
@bus.on('serial/event')
def _bus_serialEvent(e):
    from .Drink import Drink
    from .. import dispenser
    
    m = _pumpRunEventPattern.match(e)
    if m:
        pump = Pump.get_or_none(Pump.id == int(m.group(1)) + 1)
        if pump:
            with pump.lock:
                _logger.info('Pump {} running'.format(pump.name()))
                if not pump.running:
                    pump.running = True
                    bus.emit('model/pump/saved', pump)
                    
        return
        
    m = _pumpStopEventPattern.match(e)
    if m:
        pump = Pump.get_or_none(Pump.id == int(m.group(1)) + 1)
        if pump:
            with pump.lock:
                pump.running = False
                if pump.timer:
                    pump.timer.cancel()
                    pump.timer = None
                steps = int(m.group(2))
                pump.lastAmount = float(steps) / config.getfloat('pumps', 'stepsPerML')
                _logger.info('Pump {} stopped, {:.2f} mL ({} steps)'.format(pump.name(), pump.lastAmount, steps))
                
                rebuildMenu = False
                
                if pump.lastAmount > 0: # forward
                
                    if pump.isLoaded(): # primed
                        pump.setState(Pump.READY)
                        bus.emit('model/ingredient/saved', pump.ingredient)
                        rebuildMenu = True
                        
                    elif pump.isReady():
                        pump.amount = units.toOther(units.toML(pump.amount, pump.units) - pump.lastAmount, pump.units)
                        if pump.amount < 0:
                            pump.amount = 0
                        if units.toML(pump.amount, pump.units) < config.getint('pumps', 'ingredientEmptyAmount'):
                            pump.setState(Pump.EMPTY)
                            rebuildMenu = True
                            bus.emit('audio/play', 'pumpEmpty', console = True)
                        
                        ingredient = pump.ingredient
                        ingredient.timesDispensed = ingredient.timesDispensed + 1
                        ingredient.amountDispensed = ingredient.amountDispensed + pump.lastAmount
                        ingredient.save()
                        
                    elif pump.isDirty():
                        pump.setState(Pump.UNUSED)

#                elif pump.lastAmount < 0: # reverse
#                
#                    if pump.isReady():
#                        pump.setState(Pump.DIRTY)
#                        bus.emit('model/ingredient/saved', pump.ingredient)
#                        rebuildMenu = True
                        
                if not pump.save():
                    bus.emit('model/pump/saved', pump)

                if rebuildMenu:
                    Drink.rebuildMenu()

            if dispenser.inSetup() and not anyPumpsRunning():
                bus.emit('lights/play', 'setupDispenseIdle')
            elif dispenser.inManual() and not anyPumpsRunning():
                bus.emit('lights/play', 'manualDispenseIdle')
            
                    
def anyPumpsRunning():
    for i, p in _pumpExtras.items():
        if p.running:
            return True
    return False
    
class PumpExtra(object):
    allAttributes = ['volume', 'running', 'previousState', 'lock', 'lastAmount', 'timer']
#    dirtyAttributes = ['running', 'lastAmount']
    
    def __init__(self, pump):
        self.id = pump.id
        
        conf = config.get('pumps', str(self.id))
        if conf:
            conf = conf.split(',')
            self.volume = float(conf[0])
        else:
            self.volume = 0
            
        self.running = False
#        self.previousState = pump.state
        self.lock = Lock()
        self.lastAmount = 0
        self.timer = None
        self.isDirty = False
        
#    def __setattr__(self, attr, value):
#        super().__setattr__(attr, value)
#        if attr in PumpExtra.dirtyAttributes:
#            self.isDirty = True
        

class Pump(BarbotModel):
    ingredient = ForeignKeyField(Ingredient, backref = 'pump', null = True, unique = True)
    containerAmount = FloatField(default = 0)
    amount = FloatField(default = 0)
    units = CharField(default = 'ml')
    state = CharField(null = True)
    
    UNUSED = None
    LOADED = 'loaded'
    READY = 'ready'
    EMPTY = 'empty'
    DIRTY = 'dirty'
    
    @staticmethod
    def getAllPumps():
        return Pump.select()

    @staticmethod
    def getReadyPumps():
        return Pump.select().where(Pump.state == Pump.READY).execute()

    @staticmethod
    def getReadyIngredients(alternatives = True):
        ingredients = list(Ingredient.select().join(Pump).where(Pump.state == Pump.READY).execute())
        #print('base ingredients: {}'.format([(i.id, i.name) for i in ingredients]))
        if alternatives:
            ingredients = Ingredient.expandAlternatives(ingredients)
            #print('expanded ingredients: {}'.format([(i.id, i.name) for i in ingredients]))
        return ingredients
        
    @staticmethod
    def getPumpWithIngredient(ingredient, alternatives = True):
        pump = ingredient.pump.first()
        if pump and pump.state == Pump.READY:
            return pump
        if alternatives:
            for alt in ingredient.prioritizedAlternatives():
                pump = alt.alternative.pump.first()
                if pump and pump.state == Pump.READY:
                    return pump
        return None
    
    # override
    def save(self, *args, **kwargs):
            
        if self.isLoaded() or self.isReady():
            if not self.containerAmount:
                raise ModelError('container amount is required')
            if not self.amount:
                raise ModelError('amount is required')
            if not self.units:
                raise ModelError('units is required')
            if units.toML(self.amount, self.units) > units.toML(self.containerAmount, self.units):
                raise ModelError('amount must be less than container amount')
            if not self.ingredient:
                raise ModelError('ingredient is required')
            i = Pump.select().where(Pump.ingredient == self.ingredient).first()
            if i and self.id != i.id:
                raise ModelError('That ingredient is already loaded on another pump!')

        if super().save(*args, **kwargs):
            bus.emit('model/pump/saved', self)
            return True
        else:
            return False
        
    # override
    def delete_instance(self, *args, **kwargs):
        raise ModelError('pumps cannot be deleted!')
    
    def isUnused(self):
        return self.state == Pump.UNUSED
        
    def isLoaded(self):
        return self.state == Pump.LOADED
        
    def isReady(self):
        return self.state == Pump.READY
        
    def isEmpty(self):
        return self.state == Pump.EMPTY
        
    def isDirty(self):
        return self.state == Pump.DIRTY

    def setState(self, state):
        if state == self.state: return
        newState = None
        if self.isUnused():
            if state == Pump.LOADED:
                newState = state
        elif self.isLoaded():
            if state == Pump.READY:
                newState = state
            elif state == Pump.UNUSED:
                self.state = state
                return
        elif self.isReady():
            if state == Pump.EMPTY:
                newState = state
            elif state == Pump.DIRTY:
                newState = state
        elif self.isEmpty():
            if state == Pump.READY:
                newState = state
            elif state == Pump.DIRTY:
                newState = state
        elif self.isDirty():
            if state == Pump.UNUSED:
                self.state = state
                return

        if newState:
#            self.previousState = self.state
            self.state = newState
        else:
            raise ModelError('Invalid pump state transition: {} to {}'.format(self.state, state))
        
    def load(self, ingredient, containerAmount, units, amount):
        if self.isUnused():
            self.setState(Pump.LOADED)
        elif self.isEmpty():
            self.setState(Pump.READY)
        self.ingredient = ingredient
        self.containerAmount = containerAmount
        self.units = units
        self.amount = amount
        self.save()
    
    def unload(self):
        self.setState(Pump.UNUSED)
        ing = self.ingredient
        ing.lastContainerAmount = self.containerAmount
        ing.lastAmount = self.amount
        ing.lastUnits = self.units
        ing.save()
        self.ingredient = None
        self.containerAmount = 0
        self.amount = 0
        self.units = 'ml'
        self.save()
    
    def prime(self):
        amount = self.volume * config.getfloat('pumps', 'primeFactor')
        self.start(amount, forward = True)
        
    def drain(self):
        from .Drink import Drink
        amount = self.volume * config.getfloat('pumps', 'drainFactor')
        self.start(amount, forward = False)
        if not self.isUnused():
            self.setState(Pump.DIRTY)
            ing = self.ingredient
            ing.lastContainerAmount = self.containerAmount
            ing.lastAmount = self.amount
            ing.lastUnits = self.units
            ing.save()
            self.ingredient = None
            self.containerAmount = 0
            self.amount = 0
            self.units = 'ml'
            self.save()
            Drink.rebuildMenu()

    def clean(self):
        amount = self.volume * config.getfloat('pumps', 'cleanFactor')
        self.start(amount, forward = True)
        
            
#    def startAsync(self, amount = 0, forward = True):
#        threading.Thread(target = self.start, name = 'PumpThread-{}'.format(self.id), args = [amount, forward], daemon = True).start()
    
    # amount is ml, or 0 for continuous
    def start(self, amount = 0, forward = True):
        if amount:
            amount = abs(float(amount))
            steps = int(amount * config.getfloat('pumps', 'stepsPerML'))
            if not forward: steps = -steps
            _logger.info('Pump {} {} {} ml ({} steps)'.format(self.name(), 'forward' if forward else 'reverse', amount, steps))
        else:
            steps = 1
            if not forward: steps = -steps
            _logger.info('Pump {} {}'.format(self.name(), 'forward' if forward else 'reverse'))
        
        with self.lock:
            try:
                serial.write('PP{},{},{},{}'.format(
                    self.id - 1,
                    steps,
                    config.getint('pumps', 'speed'),
                    config.getint('pumps', 'acceleration')
                ))
                
                # start a timer to stop the pump
                self.timer = Timer(config.getfloat('pumps', 'limitRunTime'), self.timerStop)
                self.timer.start()
                
                # need to set running here so that dispenser can properly detect it
                self.running = True
                bus.emit('model/pump/saved', self)
                
            except serial.SerialError as e:
                _logger.error('Pump error: {}'.format(str(e)))
        
    def timerStop(self):
        _logger.warning('Pump {} stop due to timer expiration!'.format(self.name()))
        self.stop()
        
    def stop(self):
        _logger.info('Pump {} stop'.format(self.name()))

        with self.lock:
            try:
                serial.write('PH{}'.format(self.id - 1))
                #self.running = False
                if self.timer:
                    self.timer.cancel()
                    self.timer = None
                #self.save()
            except serial.SerialError as e:
                _logger.error('Pump error: {}'.format(str(e)))
    
    def name(self):
        return '#' + str(self.id)
    
    def toDict(self, ingredient = False):
        out = {
            'id': self.id,
            'name': self.name(),
            'containerAmount': self.containerAmount,
            'amount': self.amount,
            'units': self.units,
            'state': self.state,
            'running': self.running,
            'lastAmount': self.lastAmount,
        }
        if ingredient:
            if self.ingredient:
                out['ingredient_id'] = self.ingredient.id
                out['ingredient'] = self.ingredient.toDict()
            else:
                out['ingredient'] = None
        return out

    def __getattr__(self, attr):
        if attr == 'pumpExtra':
            if self.id not in _pumpExtras:
                _pumpExtras[self.id] = PumpExtra(self)
            return _pumpExtras[self.id]
        if attr in PumpExtra.allAttributes:
            return getattr(self.pumpExtra, attr)
        return super().__getattr__(attr)

    def __setattr__(self, attr, value):
        if attr in PumpExtra.allAttributes:
            setattr(self.pumpExtra, attr, value)
        else:
            super().__setattr__(attr, value)
            
    class Meta:
        database = db
        only_save_dirty = True

addModel(Pump)        
