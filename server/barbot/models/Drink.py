
import logging, datetime
from peewee import *

from ..db import db, BarbotModel, ModelError, addModel
from ..bus import bus
from ..config import config
from .. import units

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
    isOnMenu = BooleanField(default = False)
    timesDispensed = IntegerField(default = 0)
    createdDate = DateTimeField(default = datetime.datetime.now)
    updatedDate = DateTimeField(default = datetime.datetime.now)
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

        # trivial case
        if not ingredients:
            for drink in menuDrinks:
                drink.isOnMenu = False
                drink.save()
                menuUpdated = True
            
        else:
            for drink in Drink.getDrinksWithIngredients(ingredients):
                # remove this drink from the existing menu drinks
                menuDrinks = [d for d in menuDrinks if d.id != drink.id]
                
                onMenu = True
                # check for all the drink's ingredients
                for di in drink.ingredients:
                    pump = Pump.getPumpWithIngredientId(di.ingredient_id)
                    if not pump or pump.state == Pump.EMPTY or units.toML(pump.amount, pump.units) < units.toML(di.amount, di.units):
                        onMenu = False
                        break
                if onMenu != drink.isOnMenu:
                    drink.isOnMenu = onMenu
                    drink.save()
                    menuUpdated = True
        
            # any drinks in the original list are no longer on the menu
            for drink in menuDrinks:
                drink.isOnMenu = False
                drink.save()
                menuUpdated = True
                
        bus.emit('drink_menuChanged')
            
        from .DrinkOrder import DrinkOrder
        DrinkOrder.updateDrinkOrders()
    
    # override
    def save(self, *args, **kwargs):
        if self.alreadyExists():
            raise ModelError('A drink with the same name already exists!')
        if self.is_dirty():
            self.updatedDate = datetime.datetime.now()
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
        if totalMLs > config.getint('client', 'drinkSizeLimit'):
            raise ModelError('Drink ingredients exceed configured limit!')
            
        isAlcoholic = False
        
        # update/remove ingredients
        for i in self.ingredients:
            found = next((di for di in drinkIngredients if di.ingredient_id == i.ingredient_id), None)
            if found:
                i.amount = found.amount
                i.units = found.units
                i.step = found.step
                i.save()
                isAlcoholic = isAlcoholic or i.ingredient.isAlcoholic
                #_logger.debug('updating ' + str(di.id))
                drinkIngredients.remove(found)
            else:
                i.delete_instance()
                #_logger.debug('deleted ' + str(i.id))
            
        # add new ingredients
        for di in drinkIngredients:
            di.save()
            isAlcoholic = isAlcoholic or di.ingredient.isAlcoholic
            #_logger.debug('add ingredient {}'.format(di.ingredient_id))
    
        self.isAlcoholic = isAlcoholic
    
    def toDict(self, glass = False, ingredients = False):
        out = {
            'id': self.id,
            'primaryName': self.primaryName,
            'secondaryName': self.secondaryName,
            'glass_id': self.glass.id,
            'instructions': self.instructions,
            'isFavorite': self.isFavorite,
            'isAlcoholic': self.isAlcoholic,
            'isOnMenu': self.isOnMenu,
            'timesDispensed': self.timesDispensed,
            'createdDate': self.createdDate.isoformat(),
            'updatedDate': self.updatedDate.isoformat(),
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
