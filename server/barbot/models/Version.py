
from peewee import *

from ..db import db, BarbotModel, addModel


class Version(BarbotModel):
    name = CharField(unique = True)
    version = IntegerField()
    
    class Meta:
        database = db
        only_save_dirty = True

addModel(Version)
