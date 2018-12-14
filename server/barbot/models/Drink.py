
import logging, datetime
from peewee import *

from ..db import db, BarbotModel, ModelError, addModel
from ..bus import bus
from ..config import config
from .. import units
from .. import settings

from .Glass import Glass
from .Pump import Pump


_logger = logging.getLogger('Models.Drink')
_menu = {}


@bus.on('server/start')
def _bus_serverStart():
    Drink.rebuildMenu()


class Drink(BarbotModel):
    primaryName = CharField()
    secondaryName = CharField(null = True)
    glass = ForeignKeyField(Glass, backref = 'drinks')
    instructions = TextField(null = True)
    isFavorite = BooleanField(default = False)
    isAlcoholic = BooleanField(default = True)
    numIngredients = IntegerField(default = 0)
    
    timesDispensed = IntegerField(default = 0)
    source = CharField(default = 'local')
    
    @staticmethod
    def getMenuDrinks():
        ids = [id for id in _menu.keys() if _menu[id]['onMenu']]
        return Drink.select().where(Drink.id.in_(ids)).execute()

    @staticmethod
    def getMenuDrinksCount():
        return len([id for id in _menu.keys() if _menu[id]['onMenu']])

    @staticmethod
    def getDrinksWithIngredients(ingredients):
        from .DrinkIngredient import DrinkIngredient
        return Drink.select(Drink).distinct().join(DrinkIngredient).where(DrinkIngredient.ingredient.in_(list(ingredients))).execute()

    @staticmethod
    def rebuildMenu():
        global _menu
        _logger.info('Rebuilding drinks menu')
        newMenu = {}
        ingredients = Pump.getReadyIngredients()
        
        if ingredients:
            
            for drink in Drink.getDrinksWithIngredients(ingredients):
                #print(drink.name())
                
                onMenu = True
                availableIngredients = 0
                # check for all the drink's ingredients
                for di in drink.ingredients:
                    pump = Pump.getPumpWithIngredient(di.ingredient)
                    if pump and units.toML(pump.amount, pump.units) >= units.toML(di.amount, di.units):
                        #if di.ingredient_id == pump.ingredient_id:
                        #    print('  {} found on pump {}'.format(pump.ingredient_id, pump.name()))
                        #else:
                        #    print('  {} (alt) found on pump {}'.format(pump.ingredient_id, pump.name()))
                        availableIngredients = availableIngredients + 1
                    else:
                        #print('  {} not available'.format(di.ingredient_id))
                        onMenu = False
                        
                newMenu[drink.id] = {
                    'onMenu': onMenu,
                    'missingIngredients': drink.numIngredients - availableIngredients,
                }
                
                #print('  {} of {} ingredients found'.format(availableIngredients, drink.numIngredients))
                #if onMenu:
                #    print('  On menu')
                #else:
                #    print('  Not on menu')
        
        #print('old menu: {}'.format(_menu))
        #print('new menu: {}'.format(newMenu))
        
        if _menu != newMenu:
            _menu = newMenu
            #print('menu updated')
            bus.emit('drink_menuChanged')
            from .DrinkOrder import DrinkOrder
            DrinkOrder.updateDrinkOrders()
        #else:
        #    print('menu not updated')
            
    # override
    def save(self, *args, **kwargs):
        if self.alreadyExists():
            raise ModelError('A drink with the same name already exists!')
        if self.is_dirty():
            super().save(*args, **kwargs)
            bus.emit('model/drink/saved', self)
            return True
        else:
            return False
        
    # override
    def delete_instance(self, *args, **kwargs):
        for o in self.orders:
            if o.isWaiting():
                raise ModelError('This drink has a pending order!')
        super().delete_instance(*args, **kwargs)
        bus.emit('model/drink/deleted', self)

    def alreadyExists(self):
        d = Drink.select().where(Drink.primaryName == self.primaryName, Drink.secondaryName == self.secondaryName).first()
        return d if d and self.id != d.id else None
    
    def name(self):
        return self.primaryName + (('/' + self.secondaryName) if self.secondaryName else '')
        
    def isOnMenu(self):
        if self.id not in _menu: return False
        return _menu[self.id]['onMenu']
        
    def missingIngredients(self):
        if self.id not in _menu: return self.numIngredients
        return _menu[self.id]['missingIngredients']
        
    @db.atomic()
    def setIngredients(self, drinkIngredients):

        # don't allow more than 4 ingredients in the same step
        if len(drinkIngredients) >= 4:
            for step in {di.step for di in drinkIngredients}:
                stepIngs = [di for di in drinkIngredients if di.step == step]
                if len(stepIngs) > 4:
                    raise ModelError('There can not be more than 4 ingredients in the same step!')

        # don't allow more ingredients than configured
        totalMLs = 0
        for di in drinkIngredients:
            totalMLs = totalMLs + units.toML(float(di.amount), di.units)
        # TODO: move this config value to someplace else
        if totalMLs > settings.getint('drinkSizeLimit'):
            raise ModelError('Drink ingredients exceed configured limit!')
            
        isAlcoholic = False
        numIngredients = 0
        
        # update/remove ingredients
        for i in self.ingredients:
            found = next((di for di in drinkIngredients if di.ingredient_id == i.ingredient_id), None)
            if found:
                i.amount = found.amount
                i.units = found.units
                i.step = found.step
                i.save()
                isAlcoholic = isAlcoholic or i.ingredient.isAlcoholic
                numIngredients = numIngredients + 1
                #_logger.debug('updating ' + str(di.id))
                drinkIngredients.remove(found)
            else:
                i.delete_instance()
                #_logger.debug('deleted ' + str(i.id))
            
        # add new ingredients
        for di in drinkIngredients:
            di.save()
            isAlcoholic = isAlcoholic or di.ingredient.isAlcoholic
            numIngredients = numIngredients + 1
            #_logger.debug('add ingredient {}'.format(di.ingredient_id))
    
        self.isAlcoholic = isAlcoholic
        self.numIngredients = numIngredients
        
    def toDict(self, glass = False, ingredients = False, ingredientAlternatives = False):
        out = {
            'id': self.id,
            'primaryName': self.primaryName,
            'secondaryName': self.secondaryName,
            'glass_id': self.glass.id,
            'instructions': self.instructions,
            'isFavorite': self.isFavorite,
            'isAlcoholic': self.isAlcoholic,
            'numIngredients': self.numIngredients,
            'timesDispensed': self.timesDispensed,
            'name': self.name(),
            'isOnMenu': self.isOnMenu(),
            'missingIngredients': self.missingIngredients(),
        }
        if glass:
            out['glass'] = self.glass.toDict()
        if ingredients:
            out['ingredients'] = [di.toDict(ingredient = True, ingredientAlternatives = ingredientAlternatives) for di in self.ingredients]
        return out
    
    def export(self, stats = False, compact = False):
        if compact:
            out = {
                'name': self.name()
            }
        else:
            out = {
                'primaryName': self.primaryName,
            }
            if self.secondaryName:
                out['secondaryName'] = self.secondaryName
            
        out['glass'] = '{} {} {}'.format(self.glass.size, self.glass.units, self.glass.type)
        out['ingredients'] = []
            
        if self.instructions:
            out['instructions'] = self.instructions
        if stats:
            out['isFavorite'] = self.isFavorite
            out['timesDispensed'] = self.timesDispensed
        for di in self.ingredients:
            out['ingredients'].append(di.export(compact))
        return out
    
    class Meta:
        database = db
        only_save_dirty = True
        indexes = (
            (('primaryName', 'secondaryName'), True),
        )

addModel(Drink)
