from db.models import Meal, ShoppingList
from repositories.plan_repository import PlanRepository
from services.shopping_service import shopping_service

_repo = PlanRepository()


class PlanService:

    def get_grid(self) -> dict[tuple[str, str], Meal]:
        return _repo.get_grid()

    def set_meal(self, day: str, category: str, meal_id: int) -> None:
        _repo.set_cell(day, category, meal_id)

    def clear_meal(self, day: str, category: str) -> None:
        _repo.clear_cell(day, category)

    def generate_shopping_list(self, name: str) -> ShoppingList:
        # Every distinct meal anywhere in the grid (day cells + the
        # Favorites slot, which lives in the same table) contributes its
        # ingredients once - no counting how many times a meal repeats.
        meal_ids = {meal.id for meal in _repo.get_grid().values()}
        return shopping_service.create_list(name, list(meal_ids))


plan_service = PlanService()
