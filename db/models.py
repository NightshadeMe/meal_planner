from datetime import datetime
from peewee import (
    SqliteDatabase, Model,
    CharField, TextField, FloatField, BooleanField,
    IntegerField, DateTimeField,
    ForeignKeyField,
)

# Initialised lazily in database.py
database = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = database


class Ingredient(BaseModel):
    """Shared ingredient catalog. Unique on (name, unit)."""
    name = CharField()          # stored lowercase
    unit = CharField()

    class Meta:
        table_name = "ingredient"
        indexes = ((("name", "unit"), True),)   # composite unique


class Meal(BaseModel):
    name        = CharField()
    description = TextField(default="")
    created_at  = DateTimeField(default=datetime.now)
    is_lunch    = BooleanField(default=False)
    is_dinner   = BooleanField(default=False)
    is_snack    = BooleanField(default=False)

    class Meta:
        table_name = "meal"


class MealIngredient(BaseModel):
    meal       = ForeignKeyField(Meal,       backref="ingredients",      on_delete="CASCADE")
    ingredient = ForeignKeyField(Ingredient, backref="meal_ingredients")
    quantity   = FloatField()

    class Meta:
        table_name = "meal_ingredient"


class ShoppingList(BaseModel):
    name       = CharField()
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "shopping_list"


class ShoppingListItem(BaseModel):
    shopping_list   = ForeignKeyField(ShoppingList, backref="items", on_delete="CASCADE")
    ingredient_name = CharField()          # denormalised snapshot
    unit            = CharField()
    quantity        = FloatField()
    is_purchased    = BooleanField(default=False)
    is_custom       = BooleanField(default=False)  # manually added, not from a meal
    source_meal_id  = IntegerField(null=True)       # traceability only

    class Meta:
        table_name = "shopping_list_item"


class PlannedMeal(BaseModel):
    """One cell of the weekly plan grid. A missing row means an empty cell."""
    day      = CharField()   # one of constants.DAYS
    category = CharField()   # one of constants.CATEGORIES
    meal     = ForeignKeyField(Meal, backref="planned_slots", on_delete="CASCADE")

    class Meta:
        table_name = "planned_meal"
        indexes = ((("day", "category"), True),)   # composite unique


ALL_MODELS = [Ingredient, Meal, MealIngredient, ShoppingList, ShoppingListItem, PlannedMeal]
