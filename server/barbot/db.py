
from peewee import SqliteDatabase, Model, logging
from playhouse.migrate import *

from .config import config
from .app import app


_logger = logging.getLogger('DB')


models = []
version = 1

db = SqliteDatabase(config.getpath('db', 'dbFile'), pragmas = {
    'journal_mode': 'wal',  # allow readers and writers to co-exist
    'cache_size': 10000,    # 10000 pages, or ~40MB
    'foreign_keys': 1,      # enforce foreign-key constraints
    'ignore_check_constraints' : 0  # enforce CHECK constraints
})

def connect():
    db.connect()

class BarbotModel(Model):
    pass

class ModelError(Exception):
    pass
    
def addModel(cls):
    models.append(cls)
    
@app.before_request
def _connect_db():
    db.connect(reuse_if_open = True)
    return None

@app.after_request
def _close_db(r):
    if not db.is_closed():
        db.close()
    return r

def initializeDB():
    from . import models as modelsModule
    from .models.Version import Version
    
    connect()
    db.create_tables(models)

    v = Version.get_or_none(Version.name == 'db')
    if not v:
        # new database
        v = Version()
        v.name = 'db'
        v.version = version
        v.save()
        _logger.info('Database initialized')
        return
        
    if v.version == version:
        _logger.info('Database is up-to-date')
        return

    _logger.info('Upgrading database')
    
    #
    # do upgrades here
    #
    
    #if v.version == 1:
    #    _upgrade_1to2(v)
    
    _logger.info('Database upgrade complete')

#def _upgrade_1to2(v):
#    from .models.Drink import Drink
#    
#    db.execute_sql('pragma foreign_keys=off')
#    
#    with db.atomic() as transaction:
#        db.execute_sql('alter table drink rename TO drink_old')
#        db.create_tables([Drink])
#        db.execute_sql('insert into drink (primaryName, secondaryName, glass_id, instructions, isFavorite, isAlcoholic, isOnMenu, timesDispensed, source, numIngredients) ' +
#                       'select primaryName, secondaryName, glass_id, instructions, isFavorite, isAlcoholic, isOnMenu, timesDispensed, source, 0 from drink_old')
#        db.execute_sql('drop table drink_old')
#        
#        for drink in Drink.select():
#            drink.numIngredients = drink.ingredients.select().count()
#            drink.save()
#            
#        v.version = 2
#        v.save()
#        
#    db.execute_sql('pragma foreign_keys=on')

    
#    migrator = SqliteMigrator(db)
 
#    drink_numIngredients = IntegerField(default = 0)
#    drink_numIngredientsAvailable = IntegerField(null = True)
    
#    migrate(
#        migrator.drop_column('drink', 'createdDate'),
#        migrator.drop_column('drink', 'updatedDate'),
#        migrator.add_column('drink', 'numIngredients', drink_numIngredients),
#        migrator.add_column('drink', 'numIngredientsAvailable', drink_numIngredientsAvailable),
#    )

#    _logger.info('Upgraded database from version 1 to 2')
    
    