import json
from db.models import Meal, MealIngredient
from repositories.meal_repository import MealRepository
from constants import QR_FORMAT, CATEGORIES

_repo = MealRepository()


class MealService:

    def get_all(self) -> list[Meal]:
        return _repo.get_all()

    def get_by_id(self, meal_id: int) -> Meal | None:
        return _repo.get_by_id(meal_id)

    def get_ingredients(self, meal_id: int) -> list[MealIngredient]:
        return _repo.get_ingredients(meal_id)

    def get_ingredient_counts(self, meal_ids: list[int]) -> dict[int, int]:
        return _repo.get_ingredient_counts(meal_ids)

    def create(self, name: str, description: str,
               ingredients: list[dict], categories: list[str]) -> Meal:
        return _repo.create(name, description, ingredients, categories)

    def update(self, meal_id: int, name: str, description: str,
               ingredients: list[dict], categories: list[str]) -> Meal:
        return _repo.update(meal_id, name, description, ingredients, categories)

    def delete(self, meal_id: int) -> None:
        _repo.delete(meal_id)

    def get_by_category(self, category: str) -> list[Meal]:
        return _repo.get_by_category(category)

    def categories_of(self, meal: Meal) -> list[str]:
        return [c for c in CATEGORIES if getattr(meal, f"is_{c}")]

    def name_exists(self, name: str, exclude_id: int | None = None) -> bool:
        return _repo.exists_by_name(name, exclude_id)

    def to_qr_payload(self, meal_id: int) -> str:
        meal        = _repo.get_by_id(meal_id)
        ingredients = _repo.get_ingredients(meal_id)
        payload = {
            "fmt":  QR_FORMAT,
            "name": meal.name,
            "desc": meal.description,
            "cat":  self.categories_of(meal),
            "ing":  [
                {
                    "n": mi.ingredient.name,
                    "q": mi.quantity,
                    "u": mi.ingredient.unit,
                }
                for mi in ingredients
            ],
        }
        return json.dumps(payload, separators=(",", ":"))


meal_service = MealService()