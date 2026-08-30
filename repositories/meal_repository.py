from peewee import fn
from db.models import Meal, MealIngredient, Ingredient
from repositories.ingredient_repository import IngredientRepository

_ing_repo = IngredientRepository()


class MealRepository:

    def get_all(self) -> list[Meal]:
        return list(Meal.select().order_by(Meal.name))

    def get_by_id(self, meal_id: int) -> Meal | None:
        try:
            return Meal.get_by_id(meal_id)
        except Meal.DoesNotExist:
            return None

    def get_ingredients(self, meal_id: int) -> list[MealIngredient]:
        return list(
            MealIngredient
            .select(MealIngredient, Ingredient)
            .join(Ingredient)
            .where(MealIngredient.meal_id == meal_id)
        )

    def get_ingredient_counts(self, meal_ids: list[int]) -> dict[int, int]:
        """
        Return {meal_id: ingredient_count} for all given ids in one query
        instead of one query per meal (eliminates N+1 on the meal list screen).
        """
        if not meal_ids:
            return {}
        rows = (
            MealIngredient
            .select(MealIngredient.meal_id, fn.COUNT(MealIngredient.id).alias("cnt"))
            .where(MealIngredient.meal_id.in_(meal_ids))
            .group_by(MealIngredient.meal_id)
            .tuples()
        )
        return {mid: cnt for mid, cnt in rows}

    def exists_by_name(self, name: str, exclude_id: int | None = None) -> bool:
        q = Meal.select().where(Meal.name == name.strip())
        if exclude_id is not None:
            q = q.where(Meal.id != exclude_id)
        return q.exists()

    def create(self, name: str, description: str, ingredients: list[dict],
               categories: list[str]) -> Meal:
        meal = Meal.create(
            name        = name.strip(),
            description = description.strip(),
            is_lunch    = "lunch"  in categories,
            is_dinner   = "dinner" in categories,
            is_snack    = "snack"  in categories,
        )
        self._persist_ingredients(meal, ingredients)
        return meal

    def update(self, meal_id: int, name: str, description: str,
               ingredients: list[dict], categories: list[str]) -> Meal:
        meal             = Meal.get_by_id(meal_id)
        meal.name        = name.strip()
        meal.description = description.strip()
        meal.is_lunch    = "lunch"  in categories
        meal.is_dinner   = "dinner" in categories
        meal.is_snack    = "snack"  in categories
        meal.save()
        MealIngredient.delete().where(MealIngredient.meal_id == meal_id).execute()
        self._persist_ingredients(meal, ingredients)
        return meal

    def delete(self, meal_id: int) -> None:
        Meal.delete_by_id(meal_id)

    def get_by_category(self, category: str) -> list[Meal]:
        field = getattr(Meal, f"is_{category}")
        return list(Meal.select().where(field == True).order_by(Meal.name))  # noqa: E712

    def _persist_ingredients(self, meal: Meal, ingredients: list[dict]) -> None:
        for item in ingredients:
            if not item.get("name"):
                continue
            ingredient = _ing_repo.get_or_create(item["name"], item["unit"])
            MealIngredient.create(
                meal=meal,
                ingredient=ingredient,
                quantity=float(item["quantity"]),
            )