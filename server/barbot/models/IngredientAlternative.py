
import logging
from peewee import *

from ..db import db, BarbotModel, addModel
from ..bus import bus
from .Ingredient import Ingredient


_logger = logging.getLogger('Models.IngredientAlternative')


class IngredientAlternative(BarbotModel):
    ingredient = ForeignKeyField(Ingredient, backref = 'alternatives', on_delete = 'CASCADE', on_update = 'CASCADE')
    alternative = ForeignKeyField(Ingredient, backref = 'alternative_for', on_delete = 'CASCADE', on_update = 'CASCADE')

    def toDict(self, ingredient = False, alternative = False):
        out = {
            'id': self.id,
            'ingredient_id': self.ingredient_id,
            'alternative_id': self.alternative_id,
        }
        if ingredient:
            out['ingredient'] = self.ingredient.toDict()
        if alternative:
            out['alternative'] = self.alternative.toDict()
        return out
        
#    def export(self):
#        return {
#            'alternative_id': self.alternative_id,
#        }
        
    class Meta:
        database = db
        only_save_dirty = True
        indexes = (
            (('ingredient', 'alternative'), True),
        )

addModel(IngredientAlternative)
