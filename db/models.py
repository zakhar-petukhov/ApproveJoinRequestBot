from peewee import Model, IntegerField, BooleanField, FloatField, CharField, DateTimeField
from db.connection import database


# Base model bound to the shared database
class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    user_id = IntegerField(primary_key=True, unique=True)
    active = BooleanField(default=True)


class Price(BaseModel):
    name = CharField(max_length=10, primary_key=True, unique=True)
    price = FloatField()
    change = CharField(max_length=10)
    date_update = DateTimeField()

