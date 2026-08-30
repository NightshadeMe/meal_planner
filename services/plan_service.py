from itertools import groupby

from db.models import Meal, ShoppingList
from constants import DAYS, CATEGORIES
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

    def _contributing_meal_ids(self) -> list[int]:
        """
        Walk each category column Monday->Sunday independently. Empty cells
        are skipped over (they don't break a run). Consecutive occurrences
        of the identical meal (ignoring those gaps) count once; a different
        meal starts a new run, so the same meal reappearing later counts
        again.
        """
        grid = _repo.get_grid()
        contributions: list[int] = []

        for category in CATEGORIES:
            ordered_ids = [
                grid[(day, category)].id
                for day in DAYS
                if (day, category) in grid
            ]
            for meal_id, _run in groupby(ordered_ids):
                contributions.append(meal_id)

        return contributions

    def generate_shopping_list(self, name: str) -> ShoppingList:
        meal_ids = self._contributing_meal_ids()
        return shopping_service.create_list(name, meal_ids)


plan_service = PlanService()
