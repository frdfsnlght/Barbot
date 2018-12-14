
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
    
    @staticmethod
    def expandAlternatives(ingredients):
        for ingredient in ingredients[:]:
            for alt in ingredient.prioritizedAlternatives():
                if next((i for i in ingredients if i.id == alt.alternative_id), None) is None:
                    ingredients.append(alt.alternative)
        return ingredients
        
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
    
    @db.atomic()
    def setAlternatives(self, ingredientAlternatives):

        for ia in ingredientAlternatives:
            if ia.alternative_id == self.id:
                raise ModelError('Ingredient can\'t be it\'s own alternative!')
    
        alternativesChanged = False
        
        # update/remove ingredients
        for i in self.alternatives:
            found = next((ia for ia in ingredientAlternatives if ia.alternative_id == i.alternative_id), None)
            if found:
                i.priority = found.priority
                if i.save():
                    alternativesChanged = True
                ingredientAlternatives.remove(found)
            else:
                i.delete_instance()
                alternativesChanged = True
            
        # add new ingredients
        for ia in ingredientAlternatives:
            ia.save()
            alternativesChanged = True
        
        if alternativesChanged:
            bus.emit('model/ingredient/saved', self)
        
    def prioritizedAlternatives(self):
        from .IngredientAlternative import IngredientAlternative
        return self.alternatives.order_by(IngredientAlternative.priority)
        
    def allDrinks(self):
        drinks = [di.drink for di in self.drinks]
        for alt in self.alternatives:
            for di in alt.alternative.drinks:
                if not next((d for d in drinks if d.id == di.drink_id), None):
                    drinks.append(di.drink)
        return drinks
    
    def toDict(self, drinks = False, alternatives = False):
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
            out['drinks'] = [drink.toDict() for drink in self.allDrinks()]
        if alternatives:
            out['alternatives'] = [alt.toDict() for alt in self.prioritizedAlternatives()]
        
        return out
        
    def export(self, alternatives = False, compact = False, stats = False):
        out = {
            'name': self.name,
        }
        if self.isAlcoholic or not compact:
            out['isAlcoholic'] = self.isAlcoholic
        if alternatives:
            alts = [alt.alternative.name for alt in self.prioritizedAlternatives()]
            if alts:
                out['alternatives'] = alts
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
