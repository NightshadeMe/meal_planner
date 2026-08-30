from db.models import ShoppingList, ShoppingListItem


class ShoppingRepository:

    def get_all_lists(self) -> list[ShoppingList]:
        return list(ShoppingList.select().order_by(ShoppingList.created_at.desc()))

    def get_list_by_id(self, list_id: int) -> ShoppingList | None:
        try:
            return ShoppingList.get_by_id(list_id)
        except ShoppingList.DoesNotExist:
            return None

    def get_items(self, list_id: int) -> list[ShoppingListItem]:
        return list(
            ShoppingListItem.select()
            .where(ShoppingListItem.shopping_list_id == list_id)
            .order_by(
                ShoppingListItem.is_purchased,
                ShoppingListItem.ingredient_name,
            )
        )

    def item_count(self, list_id: int) -> int:
        return (ShoppingListItem
                .select()
                .where(ShoppingListItem.shopping_list_id == list_id)
                .count())

    def create_list(self, name: str) -> ShoppingList:
        return ShoppingList.create(name=name.strip())

    def delete_list(self, list_id: int) -> None:
        ShoppingList.delete_by_id(list_id)

    def add_item(self, list_id: int, ingredient_name: str, unit: str,
                 quantity: float, is_custom: bool = False,
                 source_meal_id: int | None = None) -> ShoppingListItem:
        """
        If an item with the same name+unit already exists in this list,
        aggregate quantity instead of inserting a duplicate row.
        """
        name = ingredient_name.strip().lower()
        existing = ShoppingListItem.get_or_none(
            (ShoppingListItem.shopping_list_id == list_id) &
            (ShoppingListItem.ingredient_name == name) &
            (ShoppingListItem.unit == unit)
        )
        if existing:
            existing.quantity += quantity
            existing.save()
            return existing

        return ShoppingListItem.create(
            shopping_list_id = list_id,
            ingredient_name  = name,
            unit             = unit,
            quantity         = quantity,
            is_custom        = is_custom,
            source_meal_id   = source_meal_id,
        )

    def update_quantity(self, item_id: int, quantity: float) -> None:
        ShoppingListItem.update(quantity=quantity).where(
            ShoppingListItem.id == item_id
        ).execute()

    def toggle_purchased(self, item_id: int, purchased: bool) -> None:
        ShoppingListItem.update(is_purchased=purchased).where(
            ShoppingListItem.id == item_id
        ).execute()

    def delete_item(self, item_id: int) -> None:
        ShoppingListItem.delete_by_id(item_id)

    def clear_purchased(self, list_id: int) -> None:
        ShoppingListItem.delete().where(
            (ShoppingListItem.shopping_list_id == list_id) &
            (ShoppingListItem.is_purchased == True)  # noqa: E712
        ).execute()