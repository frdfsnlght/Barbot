
import logging
from peewee import *

from ..db import db, BarbotModel, addModel
from ..bus import bus
from .Drink import Drink
from .Ingredient import Ingredient


logger = logging.getLogger('Models.DrinkIngredient')


class DrinkIngredient(BarbotModel):
    drink = ForeignKeyField(Drink, backref = 'ingredients', on_delete = 'CASCADE', on_update = 'CASCADE')
    ingredient = ForeignKeyField(Ingredient, backref = 'drinks', on_delete = 'CASCADE', on_update = 'CASCADE')
    amount = FloatField()
    units = CharField()
    step = IntegerField(default = 1)

    def ingredientName(self):
        return str(self.amount) + ' ' + self.units + ' ' + self.ingredient.name

    def toDict(self, drink = False, ingredient = False, ingredientAlternatives = False):
        out = {
            'id': self.id,
            'drink_id': self.drink_id,
            'ingredient_id': self.ingredient_id,
            'amount': self.amount,
            'units': self.units,
            'step': self.step,
        }
        if drink:
            out['drink'] = self.drink.toDict()
        if ingredient:
            out['ingredient'] = self.ingredient.toDict(alternatives = ingredientAlternatives)
        return out
        
    def export(self, compact = False):
        if compact:
            return '{}. {} {} {}'.format(self.step, self.amount, self.units, self.ingredient.name)
        else:
            return {
                'ingredient': self.ingredient.name,
                'amount': self.amount,
                'units': self.units,
                'step': self.step,
            }
        
    class Meta:
        database = db
        only_save_dirty = True
        indexes = (
            (('drink', 'ingredient'), True),
        )

addModel(DrinkIngredient)
