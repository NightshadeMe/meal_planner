from db.models import PlannedMeal, Meal


class PlanRepository:

    def get_grid(self) -> dict[tuple[str, str], Meal]:
        """Return {(day, category): Meal} for every currently-planned cell."""
        grid: dict[tuple[str, str], Meal] = {}
        for pm in PlannedMeal.select(PlannedMeal, Meal).join(Meal):
            grid[(pm.day, pm.category)] = pm.meal
        return grid

    def set_cell(self, day: str, category: str, meal_id: int) -> None:
        existing = PlannedMeal.get_or_none(
            (PlannedMeal.day == day) & (PlannedMeal.category == category)
        )
        if existing:
            existing.meal_id = meal_id
            existing.save()
        else:
            PlannedMeal.create(day=day, category=category, meal_id=meal_id)

    def clear_cell(self, day: str, category: str) -> None:
        PlannedMeal.delete().where(
            (PlannedMeal.day == day) & (PlannedMeal.category == category)
        ).execute()
