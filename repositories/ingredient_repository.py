from db.models import Ingredient


class IngredientRepository:

    def get_or_create(self, name: str, unit: str) -> Ingredient:
        ingredient, _ = Ingredient.get_or_create(
            name=name.strip().lower(),
            unit=unit,
        )
        return ingredient

    def search_by_name(self, query: str) -> list[Ingredient]:
        """Return ingredients whose name starts with *query* (case-insensitive)."""
        return list(
            Ingredient.select()
            .where(Ingredient.name.contains(query.strip().lower()))
            .order_by(Ingredient.name)
            .limit(8)
        )

    def get_all(self) -> list[Ingredient]:
        return list(Ingredient.select().order_by(Ingredient.name))

    def get_by_name(self, name: str) -> Ingredient | None:
        try:
            return Ingredient.get(Ingredient.name == name.strip().lower())
        except Ingredient.DoesNotExist:
            return None
