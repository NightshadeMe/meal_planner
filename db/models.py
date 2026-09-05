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
    """Shared ingredient catalog, used for meal-creation autosuggest."""
    name = CharField(unique=True)          # stored lowercase

    class Meta:
        table_name = "ingredient"


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
    """Links a meal to an ingredient it needs. No quantity - that's decided
    per shopping trip, not baked into the recipe."""
    meal       = ForeignKeyField(Meal,       backref="ingredients",      on_delete="CASCADE")
    ingredient = ForeignKeyField(Ingredient, backref="meal_ingredients")

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
    quantity        = FloatField()
    is_purchased    = BooleanField(default=False)
    is_custom       = BooleanField(default=False)  # manually added, not from a meal
    source_meal_id  = IntegerField(null=True)       # traceability only

    class Meta:
        table_name = "shopping_list_item"


class PlannedMeal(BaseModel):
    """One cell of the weekly plan grid. A missing row means an empty cell.

    Also holds the single Favorites slot, via the sentinel pair
    (constants.FAVORITES_DAY, constants.FAVORITES_CATEGORY) - not a real
    day or category, just another row in the same table."""
    day      = CharField()   # one of constants.DAYS, or FAVORITES_DAY
    category = CharField()   # one of constants.CATEGORIES, or FAVORITES_CATEGORY
    meal     = ForeignKeyField(Meal, backref="planned_slots", on_delete="CASCADE")

    class Meta:
        table_name = "planned_meal"
        indexes = ((("day", "category"), True),)   # composite unique


ALL_MODELS = [Ingredient, Meal, MealIngredient, ShoppingList, ShoppingListItem, PlannedMeal]
