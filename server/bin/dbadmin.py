#!/usr/bin/python3

import sys, os, argparse, yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import barbot.config

config = barbot.config.load()

import barbot.units
barbot.units.load()

from barbot.db import db, initializeDB, ModelError
from barbot.models.Glass import Glass
from barbot.models.Ingredient import Ingredient
from barbot.models.DrinkIngredient import DrinkIngredient
from barbot.models.Drink import Drink


args = None

class DBAdminError(Exception):
    pass

    
def doExport(args):
    
    glasses = Glass.select().where(Glass.source == args.source)
    print('Found {} glasses'.format(len(glasses)))
    
    ingredients = Ingredient.select().where(Ingredient.source == args.source)
    print('Found {} ingredients'.format(len(ingredients)))
    
    drinks = Drink.select().where(Drink.source == args.source)
    print('Found {} drinks'.format(len(drinks)))

    # add all non-source glasses and ingredients used
    for drink in drinks:
        if drink.glass.source != args.source:
            if not [glass for glass in glasses if glass.id == drink.glass_id]:
                print('Adding glass {}'.format(drink.glass.name()))
                glasses.append(drink.glass)
                
        for di in drink.ingredients:
            if di.ingredient.source != args.source:
                if not [ingredient for ingredient in ingredients if ingredient.id == di.ingredient_id]:
                    print('Adding ingredient {}'.format(di.ingredient.name))
                    ingredients.append(di.ingredient)
        
    data = {}
    data['glasses'] = [glass.export() for glass in glasses]
    data['ingredients'] = [ingredient.export(stats = args.stats) for ingredient in ingredients]
    data['drinks'] = [drink.export(stats = args.stats) for drink in drinks]
    
    print('Writing {}...'.format(args.file))
    with open(args.file, 'w') as file:
        file.write(yaml.dump(data, default_flow_style = False))
        
    print('Wrote {} glasses'.format(len(data['glasses'])))
    print('Wrote {} ingredients'.format(len(data['ingredients'])))
    print('Wrote {} drinks'.format(len(data['drinks'])))
    
    print('Done')


@db.atomic()
def doImport(args):

    print('Reading {}...'.format(args.file))
    with open(args.file, 'r') as file:
        data = yaml.load(file)
        
    print('Read {} glasses'.format(len(data['glasses'])))
    print('Read {} ingredients'.format(len(data['ingredients'])))
    print('Read {} drinks'.format(len(data['drinks'])))
        
    if args.delete:
        print('Deleting all glasses, ingredients, and drinks...')
        deleteAll()
        
    try:
        glassesCount = importGlasses(data['glasses'])
        ingredientsCount = importIngredients(data['ingredients'])
        drinksCount = importDrinks(data['drinks'], data['glasses'], data['ingredients'])
    except DBAdminError as e:
        print(str(e))
        sys.exit(1)
        
    print('Saved {} glasses'.format(glassesCount))
    print('Saved {} ingredients'.format(ingredientsCount))
    print('Saved {} drinks'.format(drinksCount))

    print('Done')
    
def deleteAll():
    DrinkIngredient.delete().execute()
    Drink.delete().execute()
    Ingredient.delete().execute()
    Glass.delete().execute()

def importGlasses(glasses):
    count = 0
    for glass in glasses:
        try:
            g = Glass()
            g.type = glass['type']
            g.size = glass['size']
            g.units = glass['units']
            if 'description' in glass:
                g.description = glass['description']
            g.source = args.source
            og = g.alreadyExists()
            if og:
                g = og
                print('Glass "{}" already exists'.format(g.name()))
            else:
                g.save()
                count = count + 1
            glass['local_id'] = g.id
        except ModelError as e:
            raise DBAdminError('Glass "{}": {}'.format(glass['type'], str(e)))
    return count

def importIngredients(ingredients):
    count = 0
    for ingredient in ingredients:
        try:
            i = Ingredient()
            i.name = ingredient['name']
            if 'isAlcoholic' in ingredient:
                i.isAlcoholic = ingredient['isAlcoholic']
            if args.stats:
                if 'timesDispensed' in ingredient:
                    i.timesDispensed = ingredient['timesDispensed']
                if 'amountDispensed' in ingredient:
                    i.amountDispensed = ingredient['amountDispensed']
            i.source = args.source
            oi = i.alreadyExists()
            if oi:
                i = oi
                print('Ingredient "{}" already exists'.format(i.name))
            else:
                i.save()
                count = count + 1
            ingredient['local_id'] = i.id
        except ModelError as e:
            raise DBAdminError('Ingredient "{}": {}'.format(ingredient['name'], str(e)))
    return count
    
def importDrinks(drinks, glasses, ingredients):
    count = 0
    for drink in drinks:
        try:
            d = Drink()
            d.primaryName = drink['primaryName']
            if 'secondaryName' in drink:
                d.secondaryName = drink['secondaryName']
            if 'instructions' in drink:
                d.instructions = drink['instructions']
        
            glass = [glass for glass in glasses if glass['id'] == drink['glass_id']][0]
            d.glass_id = glass['local_id']
            
            if args.stats:
                if 'isFavorite' in drink:
                    d.isFavorite = drink['isFavorite']
                if 'timesDispensed' in drink:
                    d.timesDispensed = drink['timesDispensed']
            d.source = args.source
            od = d.alreadyExists()
            if d.alreadyExists():
                print('Drink "{}" already exists'.format(d.name()))
                continue

            d.save()
                
            for drinkIngredient in drink['ingredients']:
                if 'ingredient' in drinkIngredient:
                    ingredient = Ingredient.get_or_none(Ingredient.name == drinkIngredient['ingredient'])
                    if not ingredient:
                        raise DBAdminError('Drink "{}": ingredient "{}" not found!'.format(drink['primaryName'], drinkIngredient['ingredient']))
                    drinkIngredient['ingredientId'] = ingredient.id
                else:
                    ingredient = [ingredient for ingredient in ingredients if ingredient['id'] == drinkIngredient['ingredient_id']][0]
                    drinkIngredient['ingredientId'] = ingredient['local_id']
                
            d.setIngredients(drink['ingredients'])
            
            d.save()
            count = count + 1
            
        except ModelError as e:
            raise DBAdminError('Drink "{}": {}'.format(drink['primaryName'], str(e)))
        
    return count
    
@db.atomic()
def doDelete(args):

    drinks = Drink.select().where(Drink.source == args.source)
    print('Found {} drinks'.format(len(drinks)))
    
    drinksCount = len(drinks)
    for drink in drinks:
        drink.delete_instance()
        
    ingredients = Ingredient.select().where(Ingredient.source == args.source)
    ingredientsCount = 0
    print('Found {} ingredients'.format(len(ingredients)))
    for ingredient in ingredients:
        if not ingredient.drinks:
            ingredient.delete_instance()
            ingredientsCount = ingredientsCount + 1
        else:
            print('Ingredient "{}" is still used by at least one drink'.format(ingredient.name))
        
    glasses = Glass.select().where(Glass.source == args.source)
    glassesCount = 0
    print('Found {} glasses'.format(len(glasses)))
    for glass in glasses:
        if not glass.drinks:
            glass.delete_instance()
            glassesCount = glassesCount + 1
        else:
            print('Glass "{}" is still used by at least one drink'.format(glass.name()))
    
    print('Deleted {} glasses'.format(glassesCount))
    print('Deleted {} ingredients'.format(ingredientsCount))
    print('Deleted {} drinks'.format(drinksCount))
    
def doSize(args):
    glasses = Glass.select()
    print('{} glasses'.format(len(glasses)))
    ingredients = Ingredient.select()
    print('{} ingredients'.format(len(ingredients)))
    drinks = Drink.select()
    print('{} drinks'.format(len(drinks)))

def doSources(args):
    sources = []
    
    for glass in Glass.select(Glass.source).distinct():
        if glass.source not in sources:
            sources.append(glass.source)
            
    for ingredient in Ingredient.select(Ingredient.source).distinct():
        if ingredient.source not in sources:
            sources.append(ingredient.source)
    
    for drink in Drink.select(Drink.source).distinct():
        if drink.source not in sources:
            sources.append(drink.source)
    
    sources.sort()
    for source in sources:
        print(source)
        
if __name__ == '__main__':
    initializeDB()
    
    parser = argparse.ArgumentParser(description = 'Barbot database tools')
    subparsers = parser.add_subparsers(dest = 'subparser', help = 'command help')
    
    subp = subparsers.add_parser('export', help = 'export help')
    subp.add_argument('-s', '--source', default = 'local',
                      help = 'the name of the source to export')
    subp.add_argument('--stats', action = 'store_true',
                      help = 'should ingredient/drink stats be exported')
    subp.add_argument('file',
                      help = 'the name of the output file')
    subp.set_defaults(func = doExport)

    subp = subparsers.add_parser('import', help = 'import help')
    subp.add_argument('-d', '--delete', action = 'store_true',
                      help = 'delete all data from the database first')
    subp.add_argument('--stats', action = 'store_true',
                      help = 'should ingredient/drink stats be imported')
    subp.add_argument('source',
                      help = 'the name of the source to import')
    subp.add_argument('file',
                      help = 'the name of the input file')
    subp.set_defaults(func = doImport)

    subp = subparsers.add_parser('delete', help = 'delete help')
    subp.add_argument('source',
                      help = 'the name of the source to delete')
    subp.set_defaults(func = doDelete)
    
    subp = subparsers.add_parser('size', help = 'size help')
    subp.set_defaults(func = doSize)
    
    subp = subparsers.add_parser('sources', help = 'sources help')
    subp.set_defaults(func = doSources)
    
    args = parser.parse_args()
    if args.subparser is None:
        parser.print_help()
    else:
        args.func(args)
        