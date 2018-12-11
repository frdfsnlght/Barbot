
import logging
from peewee import *

from ..db import db, BarbotModel, addModel
from ..bus import bus
from .Ingredient import Ingredient


_logger = logging.getLogger('Models.IngredientAlternative')


class IngredientAlternative(BarbotModel):
    ingredient = ForeignKeyField(Ingredient, backref = 'alternatives', on_delete = 'CASCADE', on_update = 'CASCADE')
    alternative = ForeignKeyField(Ingredient, backref = 'alternative_for', on_delete = 'CASCADE', on_update = 'CASCADE')
    priority = IntegerField(default = 0)

    # override
    def save(self, *args, **kwargs):
        saved = super().save(*args, **kwargs)
        
        # create reverse record
        rev = IngredientAlternative.select().where(IngredientAlternative.ingredient_id == self.alternative_id, IngredientAlternative.alternative_id == self.ingredient_id).first()
        if not rev:
            rev = IngredientAlternative()
            rev.ingredient_id = self.alternative_id
            rev.alternative_id = self.ingredient_id
            priority = IngredientAlternative.select(fn.MAX(IngredientAlternative.priority)).where(IngredientAlternative.ingredient_id == rev.ingredient_id).scalar()
            if priority is None:
                rev.priority = 0
            else:
                rev.priority = priority + 1
            rev.save()
        
        return saved
        
    # override
    def delete_instance(self, *args, **kwargs):
        super().delete_instance(*args, **kwargs)
        
        # delete the reverse record
        rev = IngredientAlternative.select().where(IngredientAlternative.ingredient_id == self.alternative_id, IngredientAlternative.alternative_id == self.ingredient_id).first()
        if rev:
            rev.delete_instance()
    
    # TODO: remove args
    def toDict(self, ingredient = False, alternative = False):
        return self.alternative.toDict()
        
#        out = {
#            'id': self.id,
#            'ingredient_id': self.ingredient_id,
#            'alternative_id': self.alternative_id,
#            'priority': self.priority,
#        }
#        if ingredient:
#            out['ingredient'] = self.ingredient.toDict()
#        if alternative:
#            out['alternative'] = self.alternative.toDict()
#        return out
        
    class Meta:
        database = db
        only_save_dirty = True
        indexes = (
            (('ingredient', 'alternative'), True),
        )

addModel(IngredientAlternative)
