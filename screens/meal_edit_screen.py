from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from services.meal_service import meal_service
from constants import UNITS, CATEGORIES, CATEGORY_LABELS
from utils import snackbar

Builder.load_string("""
<MealEditScreen>:
    name: "meal_edit"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: toolbar
            title: "New Meal"
            elevation: 2
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["content-save-outline", lambda x: root.save()]]

        ScrollView:
            MDBoxLayout:
                id: form
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "16dp"
                spacing: "12dp"

                MDTextField:
                    id: name_field
                    hint_text: "Meal name *"
                    mode: "rectangle"

                MDTextField:
                    id: desc_field
                    hint_text: "Description (optional)"
                    mode: "rectangle"
                    multiline: True

                MDLabel:
                    text: "Categories *"
                    font_style: "Subtitle1"
                    size_hint_y: None
                    height: "32dp"

                MDBoxLayout:
                    id: category_row
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "44dp"
                    spacing: "8dp"

                MDLabel:
                    text: "Ingredients"
                    font_style: "Subtitle1"
                    size_hint_y: None
                    height: "32dp"

                MDBoxLayout:
                    id: ingredients_container
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: "8dp"

                MDRaisedButton:
                    text: "Add Ingredient"
                    icon: "plus"
                    size_hint_x: None
                    width: "180dp"
                    on_release: root.add_ingredient_row()
""")


class MealEditScreen(MDScreen):
    _meal_id = None

    def prepare(self, meal_id: int | None) -> None:
        self._meal_id = meal_id
        Clock.schedule_once(self._setup)

    def _setup(self, *_args) -> None:
        self.ids.toolbar.title   = "Edit Meal" if self._meal_id else "New Meal"
        self.ids.name_field.text = ""
        self.ids.desc_field.text = ""
        self.ids.ingredients_container.clear_widgets()

        self._selected_categories: set[str] = set()
        self._build_category_row()

        if self._meal_id:
            meal = meal_service.get_by_id(self._meal_id)
            if meal:
                self.ids.name_field.text = meal.name
                self.ids.desc_field.text = meal.description or ""
                self._selected_categories = set(meal_service.categories_of(meal))
                self._refresh_category_buttons()
                for mi in meal_service.get_ingredients(self._meal_id):
                    self.add_ingredient_row(
                        name=mi.ingredient.name,
                        unit=mi.ingredient.unit,
                        qty=mi.quantity,
                        locked=True,
                    )

        if not self.ids.ingredients_container.children:
            self.add_ingredient_row()

    def _build_category_row(self) -> None:
        row = self.ids.category_row
        row.clear_widgets()
        self._category_buttons: dict[str, MDRaisedButton] = {}
        for cat in CATEGORIES:
            btn = MDRaisedButton(text=CATEGORY_LABELS[cat])
            btn.bind(on_release=lambda _b, c=cat: self._toggle_category(c))
            self._category_buttons[cat] = btn
            row.add_widget(btn)
        self._refresh_category_buttons()

    def _toggle_category(self, cat: str) -> None:
        if cat in self._selected_categories:
            self._selected_categories.discard(cat)
        else:
            self._selected_categories.add(cat)
        self._refresh_category_buttons()

    def _refresh_category_buttons(self) -> None:
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        for cat, btn in self._category_buttons.items():
            selected = cat in self._selected_categories
            btn.md_bg_color = app.theme_cls.primary_color if selected else (0.85, 0.85, 0.85, 1)
            btn.text_color  = (1, 1, 1, 1) if selected else (0, 0, 0, 1)

    def add_ingredient_row(self, name: str = "", unit: str = "g",
                           qty: float = 0, locked: bool = False) -> None:
        from widgets.ingredient_row import IngredientRow
        row = IngredientRow()

        def delete_row(r=row):
            self.ids.ingredients_container.remove_widget(r)

        row.request_delete = delete_row
        self.ids.ingredients_container.add_widget(row)

        if name:
            Clock.schedule_once(
                lambda _: row.populate(name, unit, qty or UNITS[unit]["min"], locked)
            )
        else:
            Clock.schedule_once(lambda _: row.ids.stepper.set_unit(unit))

    def save(self) -> None:
        name = self.ids.name_field.text.strip()
        desc = self.ids.desc_field.text.strip()

        if not name:
            snackbar("Meal name is required")
            return

        categories = [c for c in CATEGORIES if c in self._selected_categories]
        if not categories:
            snackbar("Select at least one category")
            return

        ingredients = [
            row.get_data()
            for row in self.ids.ingredients_container.children
            if row.get_data().get("name")
        ]
        if not ingredients:
            snackbar("Add at least one ingredient")
            return

        if meal_service.name_exists(name, exclude_id=self._meal_id):
            self._confirm_duplicate_name(name, desc, ingredients, categories)
            return

        self._persist(name, desc, ingredients, categories)

    def _confirm_duplicate_name(self, name, desc, ingredients, categories) -> None:
        dialog = MDDialog(
            title="Duplicate name",
            text=f"A meal named '{name}' already exists. Save anyway?",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Save",   on_release=lambda x: [
                    dialog.dismiss(), self._persist(name, desc, ingredients, categories)
                ]),
            ],
        )
        dialog.open()

    def _persist(self, name: str, desc: str, ingredients: list, categories: list[str]) -> None:
        if self._meal_id:
            meal_service.update(self._meal_id, name, desc, ingredients, categories)
        else:
            meal_service.create(name, desc, ingredients, categories)
        snackbar("Meal saved")
        self.go_back()

    def go_back(self) -> None:
        from kivymd.app import MDApp
        MDApp.get_running_app().navigate_to("meals")