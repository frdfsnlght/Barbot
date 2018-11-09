
from peewee import SqliteDatabase, Model, logging

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
    
    v.version = version
    v.save()
    _logger.info('Database upgrade complete')
