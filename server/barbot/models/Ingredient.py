
import logging
from peewee import *

from ..db import db, BarbotModel, ModelError, addModel
from ..bus import bus


_logger = logging.getLogger('Models.Ingredient')


class Ingredient(BarbotModel):
    name = CharField(unique = True)
    isAlcoholic = BooleanField(default = False)
    timesDispensed = IntegerField(default = 0)
    amountDispensed = FloatField(default = 0)
    
    lastContainerAmount = FloatField(null = True)
    lastAmount = FloatField(null = True)
    lastUnits = CharField(null = True)
    
    source = CharField(default = 'local')
    
    # override
    def save(self, *args, **kwargs):
        if self.alreadyExists():
            raise ModelError('An ingredient with the same name already exists!')
        if super().save(*args, **kwargs):
            bus.emit('model/ingredient/saved', self)
            return True
        else:
            return False
    
    # override
    def delete_instance(self, *args, **kwargs):
        if self.drinks.execute():
            raise ModelError('This ingredient is used by at least one drink!')
        super().delete_instance(*args, **kwargs)
        bus.emit('model/ingredient/deleted', self)

    def alreadyExists(self):
        i = Ingredient.select().where(Ingredient.name == self.name).first()
        return i if i and self.id != i.id else None
    
    def toDict(self, drinks = False):
        pump = self.pump.first()
        out = {
            'id': self.id,
            'name': self.name,
            'isAlcoholic': self.isAlcoholic,
            'timesDispensed': self.timesDispensed,
            'amountDispensed': self.amountDispensed,
            'isAvailable': pump and pump.isReady(),
            'lastContainerAmount': self.lastContainerAmount,
            'lastAmount': self.lastAmount,
            'lastUnits': self.lastUnits,
        }
        if drinks:
            out['drinks'] = [di.toDict(drink = True) for di in self.drinks]
        return out
        
    def export(self, stats = False):
        out = {
            'id': self.id,
            'name': self.name,
            'isAlcoholic': self.isAlcoholic,
        }
        if stats:
            out['timesDispensed'] = self.timesDispensed
            out['amountDispensed'] = self.amountDispensed
            out['lastContainerAmount'] = self.lastContainerAmount
            out['lastAmount'] = self.lastAmount
            out['lastUnits'] = self.lastUnits
        return out
    
    class Meta:
        database = db
        only_save_dirty = True

addModel(Ingredient)
