
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
    
    isOnMenu = BooleanField(default = False)
    numIngredientsAvailable = IntegerField(null = True)
    
    timesDispensed = IntegerField(default = 0)
    source = CharField(default = 'local')
    
    @staticmethod
    def getMenuDrinks():
        return Drink.select().where(Drink.isOnMenu == True).execute()

    @staticmethod
    def getDrinksWithIngredients(ingredients):
        from .DrinkIngredient import DrinkIngredient
        return Drink.select(Drink).distinct().join(DrinkIngredient).where(DrinkIngredient.ingredient.in_(list(ingredients))).execute()

    @staticmethod
    @db.atomic()
    def rebuildMenu():
        _logger.info('Rebuilding drinks menu')
        menuUpdated = False
        ingredients = Pump.getReadyIngredients()
        menuDrinks = Drink.getMenuDrinks()

        print('current menu: {}'.format([d.name() for d in menuDrinks]))
        
        # trivial case
        if not ingredients:
            for drink in menuDrinks:
                drink.isOnMenu = False
                drink.save()
                menuUpdated = True
            
        else:
            print('ingredients: {}'.format([i.name for i in ingredients]))
            
            for drink in Drink.getDrinksWithIngredients(ingredients):
                print(drink.name())
                
                # remove this drink from the existing menu drinks
                menuDrinks = [d for d in menuDrinks if d.id != drink.id]
                
                onMenu = True
                availableIngredients = 0
                # check for all the drink's ingredients
                for di in drink.ingredients:
                    pump = Pump.getPumpWithIngredientId(di.ingredient_id)
                    if pump and pump.state == Pump.READY and units.toML(pump.amount, pump.units) >= units.toML(di.amount, di.units):
                        print('  {} found on pump {}'.format(di.ingredient.name, pump.name()))
                        availableIngredients = availableIngredients + 1
                    else:
                        print('  {} not available'.format(di.ingredient.name))
                        onMenu = False
                        
                if onMenu != drink.isOnMenu or availableIngredients != drink.numIngredientsAvailable:
                    drink.isOnMenu = onMenu
                    drink.numIngredientsAvailable = availableIngredients
                    drink.save()
                    menuUpdated = True
                    
                    print('  {} of {} ingredients found'.format(drink.numIngredientsAvailable, drink.numIngredients))
                    if drink.isOnMenu:
                        print('  Added to menu')
                    else:
                        print('  Removed from menu')
                else:
                    print('  {} of {} ingredients found'.format(drink.numIngredientsAvailable, drink.numIngredients))
                    if drink.isOnMenu:
                        print('  Stays on menu')
                    else:
                        print('  Stays off menu')
        
            # any drinks in the original list are no longer on the menu
            for drink in menuDrinks:
                drink.isOnMenu = False
                drink.save()
                menuUpdated = True
                print('{} removed from menu'.format(drink.name()))
                
        if menuUpdated:
            print('menu was updated')
            bus.emit('drink_menuChanged')
            from .DrinkOrder import DrinkOrder
            DrinkOrder.updateDrinkOrders()
        else:
            print('menu was not updated')
            
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
        
    def toDict(self, glass = False, ingredients = False):
        out = {
            'id': self.id,
            'primaryName': self.primaryName,
            'secondaryName': self.secondaryName,
            'glass_id': self.glass.id,
            'instructions': self.instructions,
            'isFavorite': self.isFavorite,
            'isAlcoholic': self.isAlcoholic,
            'numIngredients': self.numIngredients,
            'isOnMenu': self.isOnMenu,
            'numIngredientsAvailable': self.numIngredientsAvailable,
            'timesDispensed': self.timesDispensed,
            'name': self.name(),
        }
        if glass:
            out['glass'] = self.glass.toDict()
        if ingredients:
            out['ingredients'] = [di.toDict(ingredient = True) for di in self.ingredients]
        return out
    
    def export(self, stats = False):
        out = {
            'primaryName': self.primaryName,
            'secondaryName': self.secondaryName,
            'glass_id': self.glass_id,
            'instructions': self.instructions,
            'ingredients': []
        }
        if stats:
            out['isFavorite'] = self.isFavorite
            out['timesDispensed'] = self.timesDispensed
        for di in self.ingredients:
            out['ingredients'].append(di.export())
        return out
    
    class Meta:
        database = db
        only_save_dirty = True
        indexes = (
            (('primaryName', 'secondaryName'), True),
        )

addModel(Drink)
