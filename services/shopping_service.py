from db.models import ShoppingList, ShoppingListItem
from repositories.meal_repository import MealRepository
from repositories.shopping_repository import ShoppingRepository

_meal_repo     = MealRepository()
_shopping_repo = ShoppingRepository()


class ShoppingService:

    # ------------------------------------------------------------------ read --

    def get_all_lists(self) -> list[ShoppingList]:
        return _shopping_repo.get_all_lists()

    def get_list_by_id(self, list_id: int) -> ShoppingList | None:
        return _shopping_repo.get_list_by_id(list_id)

    def get_items(self, list_id: int) -> list[ShoppingListItem]:
        return _shopping_repo.get_items(list_id)

    def item_count(self, list_id: int) -> int:
        return _shopping_repo.item_count(list_id)

    # ---------------------------------------------------- list generation --

    def create_list(self, name: str, meal_ids: list[int]) -> ShoppingList:
        """One row per unique ingredient across the selected meals - no
        cumulation, no rules beyond "needed at least once this week"."""
        seen: set[str] = set()

        shopping_list = _shopping_repo.create_list(name)
        for meal_id in meal_ids:
            for mi in _meal_repo.get_ingredients(meal_id):
                if mi.ingredient.name in seen:
                    continue
                seen.add(mi.ingredient.name)
                _shopping_repo.add_item(
                    list_id        = shopping_list.id,
                    ingredient_name= mi.ingredient.name,
                    quantity       = 1,
                    is_custom      = False,
                    source_meal_id = meal_id,
                )
        return shopping_list

    # --------------------------------------------------------------- items --

    def add_custom_item(self, list_id: int, ingredient_name: str,
                        quantity: float) -> ShoppingListItem:
        return _shopping_repo.add_item(
            list_id, ingredient_name, quantity, is_custom=True
        )

    def update_quantity(self, item_id: int, quantity: float) -> None:
        _shopping_repo.update_quantity(item_id, quantity)

    def toggle_purchased(self, item_id: int, purchased: bool) -> None:
        _shopping_repo.toggle_purchased(item_id, purchased)

    def delete_item(self, item_id: int) -> None:
        _shopping_repo.delete_item(item_id)

    def delete_list(self, list_id: int) -> None:
        _shopping_repo.delete_list(list_id)

    def clear_purchased(self, list_id: int) -> None:
        _shopping_repo.clear_purchased(list_id)


shopping_service = ShoppingService()
