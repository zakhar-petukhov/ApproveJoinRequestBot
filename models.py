from peewee import Model, IntegerField, BooleanField
from playhouse.sqliteq import SqliteQueueDatabase

database = SqliteQueueDatabase('db.sqlite3')


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    user_id = IntegerField(primary_key=True, unique=True)
    active = BooleanField(default=True)
