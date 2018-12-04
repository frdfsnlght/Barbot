
import logging
from peewee import *

from ..db import db, BarbotModel, ModelError, addModel
from ..bus import bus


_logger = logging.getLogger('Models.Glass')


class Glass(BarbotModel):
    type = CharField()
    size = IntegerField()
    units = CharField()
    description = TextField(null = True)
    source = CharField(default = 'local')
    
    # override
    def save(self, *args, **kwargs):
        if self.alreadyExists():
            raise ModelError('The same glass already exists!')
        return super().save(*args, **kwargs)

    # override
    def delete_instance(self, *args, **kwargs):
        if self.drinks.execute():
            raise ModelError('This glass is used by at least one drink!')
        super().delete_instance(*args, **kwargs)
            
    def alreadyExists(self):
        g = Glass.select().where(Glass.type == self.type, Glass.size == self.size, Glass.units == self.units).first()
        return g if g and self.id != g.id else None
    
    def name(self):
        return str(self.size) + ' ' + self.units + ' ' + self.type
        
    def toDict(self, drinks = False):
        out = {
            'id': self.id,
            'type': self.type,
            'size': self.size,
            'units': self.units,
            'description' : self.description,
            'name': self.name()
        }
        if drinks:
            out['drinks'] = [d.toDict() for d in self.drinks]
        return out
        
    def export(self):
        return {
            'id': self.id,
            'type': self.type,
            'size': self.size,
            'units': self.units,
            'description': self.description,
        }
        
    class Meta:
        database = db
        only_save_dirty = True
        indexes = (
            (('type', 'size', 'units'), True),
        )

addModel(Glass)
