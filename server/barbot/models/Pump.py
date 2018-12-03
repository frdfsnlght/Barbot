
import logging, time, threading, re
from peewee import *
from threading import Lock, Timer

from ..db import db, BarbotModel, ModelError, addModel
from ..config import config
from ..bus import bus
from .. import units
from .. import serial
from .Ingredient import Ingredient


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
                
                if pump.lastAmount > 0 and (pump.state == Pump.LOADED or pump.state == Pump.READY):
                    pump.amount = units.toOther(units.toML(pump.amount, pump.units) - pump.lastAmount, pump.units)
                    if pump.amount < 0:
                        pump.amount = 0
                    if units.toML(pump.amount, pump.units) < config.getint('pumps', 'ingredientEmptyAmount'):
                        pump.state = Pump.EMPTY

                pump.save()
                _logger.info('Pump {} stopped, {:.2f} mL ({} steps)'.format(pump.name(), pump.lastAmount, steps))

def anyPumpsRunning():
    for i, p in _pumpExtras.items():
        if p.running:
            return True
    return False
    
class PumpExtra(object):
    allAttributes = ['volume', 'running', 'previousState', 'lock', 'lastAmount', 'timer']
    dirtyAttributes = ['running', 'lastAmount']
    
    def __init__(self, pump):
        self.id = pump.id
        
        conf = config.get('pumps', str(self.id))
        if conf:
            conf = conf.split(',')
            self.volume = float(conf[0])
        else:
            self.volume = 0
            
        self.running = False
        self.previousState = pump.state
        self.lock = Lock()
        self.lastAmount = 0
        self.timer = None
        self.isDirty = False
        
    def __setattr__(self, attr, value):
        super().__setattr__(attr, value)
        if attr in PumpExtra.dirtyAttributes:
            self.isDirty = True
        

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
    
    setup = False
    flushing = False
    
    @staticmethod
    def getAllPumps():
        return Pump.select()

    @staticmethod
    def getReadyPumps():
        return Pump.select().where(Pump.state == Pump.READY).execute()

    @staticmethod
    def getReadyIngredients():
        return Ingredient.select().join(Pump).where(Pump.state == Pump.READY).execute()
        
    @staticmethod
    def getPumpWithIngredientId(id):
        return Pump.select().where((Pump.state == Pump.READY) & (Pump.ingredient_id == id)).first()
    
    @staticmethod
    def startSetup():
        if Pump.setup:
            raise ModelError('Pumps are already in setup!')
        if anyPumpsRunning():
            raise ModelError('At least one pump is currently running!')
        Pump.setup = True
        bus.emit('model/pump/setup')
    
    @staticmethod
    def stopSetup():
        if not Pump.setup:
            return
        Pump.setup = False
        bus.emit('model/pump/setup')
    
    @staticmethod
    def enablePump(id):
        p = Pump.get(Pump.id == id)
        p.enable()
        
    @staticmethod
    def disablePump(id):
        p = Pump.get(Pump.id == id)
        p.disable()
        
    @staticmethod
    def loadPump(params):
        p = Pump.get(Pump.id == int(params['id']))
        p.load(params)

    @staticmethod
    def unloadPump(id):
        p = Pump.get(Pump.id == id)
        p.unload()

    @staticmethod
    def primePump(params, *args, **kwargs):
        p = Pump.get(Pump.id == int(params['id']))
        p.prime(float(params['amount']) if 'amount' in params else (p.volume * config.getfloat('pumps', 'primeFactor')), *args, **kwargs)
        
    @staticmethod
    def drainPump(id, *args, **kwargs):
        p = Pump.get(Pump.id == id)
        p.drain(p.volume * config.getfloat('pumps', 'drainFactor'), *args, **kwargs)
        
    @staticmethod
    def cleanPump(params, *args, **kwargs):
        p = Pump.get(Pump.id == int(params['id']))
        p.clean(float(params['amount']) if 'amount' in params else (p.volume * config.getfloat('pumps', 'cleanFactor')), *args, **kwargs)
        
    @staticmethod
    def startFlush(ids):
        if not Pump.setup:
            raise ModelError('Pumps are not in setup!')
        if Pump.flushing:
            raise ModelError('Pumps are already flushing!')
        if anyPumpsRunning():
            raise ModelError('At least one pump is currently running!')
        
        pumps = []
        for pump in Pump.select():
            if pump.id in ids:
                if pump.state == Pump.DIRTY or pump.state == Pump.UNUSED:
                    pumps.append(pump)
                else:
                    raise ModelError('Invalid pump state!')

        try:
            serial.write('PF{}'.format(','.join([str(pump.id - 1) for pump in pumps])))
            for pump in pumps:
                pump.running = True
                pump.save()
        except serial.SerialError as e:
            _logger.error('Pump error: {}'.format(str(e)))
                
        _logger.info('Pumps {} started flush'.format(','.join([str(id) for id in ids])))
        Pump.flushing = True
        bus.emit('model/pump/flushing')
    
    @staticmethod
    def stopFlush():
        pumps = [pump for pump in Pump.select() if pump.running]
        try:
            serial.write('PF')
            for pump in pumps:
                if pump.state == Pump.DIRTY:
                    pump.state == Pump.UNUSED
                    pump.save()
        except serial.SerialError as e:
            _logger.error('Pump error: {}'.format(str(e)))
        
        _logger.info('Pumps {} stopped flush'.format(','.join([str(pump.id) for pump in pumps])))
        Pump.flushing = False
        bus.emit('model/pump/flushing')
        
    # override
    def save(self, *args, **kwargs):
            
        if self.state == Pump.LOADED or self.state == Pump.READY:
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

        emitStateChanged = False
        if 'state' in self.dirty_fields:
            emitStateChanged = True
        if super().save(*args, **kwargs) or self.pumpExtra.isDirty:
            bus.emit('model/pump/saved', self)
            self.pumpExtra.isDirty = False
            if emitStateChanged:
                bus.emit('model/pump/stateChanged', self, self.previousState)
                self.previousState = self.state
        
    # override
    def delete_instance(self, *args, **kwargs):
        raise ModelError('pumps cannot be deleted!')
    
    def isReady(self):
        return self.state == Pump.READY
        
    def load(self, params):
        if not Pump.setup:
            raise ModelError('Pumps are not in setup!')
        i = Ingredient.get_or_none(Ingredient.id == int(params['ingredientId']))
        if not i:
            raise ModelError('Ingredient not found!')
        params['ingredient'] = i
        if self.state == Pump.UNUSED:
            self.state = Pump.LOADED
            self.set(params)
            self.save()
        elif self.state == Pump.READY or self.state == Pump.EMPTY:
            self.state = Pump.READY
            self.set(params)
            self.save()
            self.ingredient.save(emitEvent = 'force')
        else:
            raise ModelError('Invalid pump state!')
    
    def unload(self):
        if not Pump.setup:
            raise ModelError('Pumps are not in setup!')
        if self.state == Pump.LOADED:
            ing = self.ingredient
            ing.lastContainerAmount = self.containerAmount
            ing.lastAmount = self.amount
            ing.lastUnits = self.units
            ing.save()
            self.state = Pump.UNUSED
            self.ingredient = None
            self.containerAmount = 0
            self.amount = 0
            self.units = 'ml'
            self.save()
        else:
            raise ModelError('Invalid pump state!')
    
    def prime(self, amount, useThread = False):
        if not Pump.setup:
            raise ModelError('Pumps are not in setup!')
        if self.state == Pump.LOADED or self.state == Pump.READY:
            if useThread:
                self.startAsync(amount, forward = True)
            else:
                self.start(amount, forward = True)
            if self.state != Pump.READY:
                self.state = Pump.READY
                self.save()
        else:
            raise ModelError('Invalid pump state!')

    def drain(self, amount, useThread = False):
        if not Pump.setup:
            raise ModelError('Pumps are not in setup!')
        if self.state == Pump.READY or self.state == Pump.EMPTY or self.state == Pump.UNUSED or self.state == Pump.DIRTY:
            if useThread:
                self.startAsync(amount, forward = False)
            else:
                self.start(amount, forward = False)
            if self.state != Pump.UNUSED:
                self.state = Pump.DIRTY
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
        else:
            raise ModelError('Invalid pump state!')

    def clean(self, amount, useThread = False):
        if not Pump.setup:
            raise ModelError('Pumps are not in setup!')
        if self.state == Pump.DIRTY or self.state == Pump.UNUSED:
            if useThread:
                self.startAsync(amount, forward = True)
            else:
                self.start(amount, forward = True)
            self.state = Pump.UNUSED
            self.save()
        else:
            raise ModelError('Invalid pump state!')

    def startAsync(self, amount = 0, forward = True):
        threading.Thread(target = self.start, name = 'PumpThread-{}'.format(self.id), args = [amount, forward], daemon = True).start()
    
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
                self.running = True
                
                # start a timer to stop the pump
                self.timer = Timer(config.getfloat('pumps', 'limitRunTime'), self.timerStop)
                self.timer.start()
                
                self.save()
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
                self.running = False
                if self.timer:
                    self.timer.cancel()
                    self.timer = None
                self.save()
            except serial.SerialError as e:
                _logger.error('Pump error: {}'.format(str(e)))
    
    def name(self):
        return '#' + str(self.id)
    
    def set(self, dict):
        if 'ingredient' in dict:
            self.ingredient = dict['ingredient']
        elif 'ingredientId' in dict:
            self.ingredient = int(dict['ingredientId'])
        if 'containerAmount' in dict:
            self.containerAmount = float(dict['containerAmount'])
        if 'units' in dict:
            self.units = str(dict['units'])
        if 'percent' in dict:
            self.amount = (float(dict['percent']) / 100) * self.containerAmount
        elif 'amount' in dict:
            self.amount = float(dict['amount'])
    
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
                out['ingredientId'] = self.ingredient.id
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
