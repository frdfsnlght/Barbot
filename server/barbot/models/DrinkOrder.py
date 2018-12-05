
import logging, datetime, os
from peewee import *

from ..db import db, BarbotModel, addModel
from ..bus import bus
from ..config import config
from .Drink import Drink
from .Pump import Pump


_logger = logging.getLogger('Models.DrinkOrder')


@bus.on('server/start')
def _bus_serverStart():
    DrinkOrder.clearSessionIds()
    
    
class DrinkOrder(BarbotModel):
    drink = ForeignKeyField(Drink, backref = 'orders', on_delete = 'CASCADE', on_update = 'CASCADE')
    name = CharField(null = True)
    createdDate = DateTimeField(default = datetime.datetime.now)
    startedDate = DateTimeField(null = True)
    completedDate = DateTimeField(null = True)
    ingredientHold = BooleanField(default = False)
    userHold = BooleanField(default = False)
    sessionId = CharField(null = True)
    
    @staticmethod
    def getFirstPending():
        try:
            return DrinkOrder.select().where(
                (DrinkOrder.startedDate.is_null()) &
                (DrinkOrder.ingredientHold == False) &
                (DrinkOrder.userHold == False)
            ).order_by(DrinkOrder.createdDate.asc()).first()
        except DoesNotExist:
            return None
    
    @staticmethod
    def getWaiting():
        return DrinkOrder.select().where(
            DrinkOrder.startedDate.is_null()
        )
    
    @staticmethod
    def deleteOldCompleted(secondsOld):
        num = DrinkOrder.delete().where(
                    DrinkOrder.completedDate < (datetime.datetime.now() - datetime.timedelta(seconds = secondsOld))
                ).execute()
        if num:
            _logger.info('Deleted {} old drink orders'.format(num))
        
    @staticmethod
    def clearSessionIds():
        DrinkOrder.update(sessionId = None).execute()
        
    # TODO: need to emit event when order changes state
    @staticmethod
    @db.atomic()
    def updateDrinkOrders():
        _logger.info('Updating drink orders')
        readyPumps = Pump.getReadyPumps()
        for o in DrinkOrder.getWaiting():
            if o.drink.isOnMenu == o.ingredientHold:
                o.ingredientHold = not o.drink.isOnMenu
                o.save()
                bus.emit('drinkOrder/changed', o)

    # override
    def save(self, *args, **kwargs):
        if super().save(*args, **kwargs):
            bus.emit('model/drinkOrder/saved', self)
            return True
        else:
            return False
        
    # override
    def delete_instance(self, *args, **kwargs):
        if self.isBeingDispensed():
            raise ModelError('This order is currently being dispensed!')
        super().delete_instance(*args, **kwargs)
        bus.emit('model/drinkOrder/deleted', self)
            
    def isWaiting(self):
        return self.startedDate is None
        
    def isBeingDispensed(self):
        return self.startedDate and self.completedDate is None
        
    def placeOnHold(self):
        self.startedDate = None
        self.userHold = True
        self.save()
        
    def desc(self):
        return '"{}" for {}'.format(self.drink.name(), self.name if self.name else 'unknown')
        
    def toDict(self, drink = False, glass = False):
        out = {
            'id': self.id,
            'drink_id': self.drink.id,
            'name': self.name,
            'createdDate': self.createdDate.isoformat(),
            'startedDate': self.startedDate.isoformat() if self.startedDate else None,
            'completedDate': self.completedDate.isoformat() if self.completedDate else None,
            'ingredientHold': self.ingredientHold,
            'userHold': self.userHold,
        }
        if drink:
            out['drink'] = self.drink.toDict(glass = glass)
        return out
        
    class Meta:
        database = db
        only_save_dirty = True

addModel(DrinkOrder)
