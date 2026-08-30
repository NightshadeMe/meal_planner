from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from constants import UNIT_LIST

Builder.load_string("""
#:import UNIT_LIST constants.UNIT_LIST

<IngredientRow>:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: "8dp", "4dp"
    spacing: "4dp"

    canvas.before:
        Color:
            rgba: (0.92, 0.92, 0.92, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]

    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: "40dp"
        spacing: "8dp"

        MDTextField:
            id: name_field
            hint_text: "Ingredient name"
            text: root.ingredient_name
            size_hint_x: 1
            mode: "rectangle"
            on_text: root._on_name_text(self.text)
            on_focus: if not self.focus: root._hide_suggestions()

        MDIconButton:
            icon: "delete-outline"
            size_hint: None, None
            size: "40dp", "40dp"
            on_release: root.request_delete()

    MDBoxLayout:
        id: suggestions_box
        orientation: "vertical"
        size_hint_y: None
        height: self.minimum_height

    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: "36dp"
        spacing: "8dp"

        Spinner:
            id: unit_spinner
            values: UNIT_LIST
            text: root.selected_unit
            size_hint: None, None
            size: "84dp", "32dp"
            disabled: root.unit_locked
            on_text: root._on_unit_change(self.text)

        QuantityStepper:
            id: stepper
            unit: root.selected_unit
            quantity: root.quantity
""")


class IngredientRow(MDBoxLayout):
    ingredient_name = StringProperty("")
    selected_unit   = StringProperty("g")
    quantity        = NumericProperty(100)
    unit_locked     = BooleanProperty(False)

    request_delete  = ObjectProperty(lambda: None)
    on_name_change  = ObjectProperty(None, allownone=True)

    _debounce_event = None

    def _on_name_text(self, text: str) -> None:
        self.ingredient_name = text
        if self.on_name_change:
            self.on_name_change(self, text)

        # Cancel any pending autocomplete lookup
        if self._debounce_event:
            self._debounce_event.cancel()
            self._debounce_event = None

        if len(text) < 2:
            self._hide_suggestions()
            return

        # Schedule lookup 300 ms after the user stops typing
        self._debounce_event = Clock.schedule_once(
            lambda _: self._do_lookup(text), 0.3
        )

    def _do_lookup(self, text: str) -> None:
        from repositories.ingredient_repository import IngredientRepository
        repo = IngredientRepository()

        # Exact match → auto-lock unit, suppress dropdown
        exact = repo.get_by_name(text.strip())
        if exact:
            self._hide_suggestions()
            if not self.unit_locked:
                self._apply_suggestion(exact)
            return

        results = repo.search_by_name(text)
        self._show_suggestions(results)

    def _on_unit_change(self, unit: str) -> None:
        self.selected_unit = unit
        self.ids.stepper.set_unit(unit)

    def _show_suggestions(self, results: list) -> None:
        from kivymd.uix.list import OneLineListItem
        box = self.ids.suggestions_box
        box.clear_widgets()
        for ing in results[:5]:
            lbl  = f"{ing.name.capitalize()}  ({ing.unit})"
            item = OneLineListItem(text=lbl, size_hint_y=None, height="40dp")
            item.bind(on_release=lambda _, i=ing: self._apply_suggestion(i))
            box.add_widget(item)

    def _hide_suggestions(self) -> None:
        self.ids.suggestions_box.clear_widgets()

    def _apply_suggestion(self, ingredient) -> None:
        self._hide_suggestions()
        self.ingredient_name       = ingredient.name
        self.selected_unit         = ingredient.unit
        self.unit_locked           = True
        self.ids.name_field.text   = ingredient.name
        self.ids.unit_spinner.text = ingredient.unit
        self.ids.stepper.set_unit(ingredient.unit)

    def get_data(self) -> dict:
        return {
            "name":     self.ingredient_name.strip(),
            "unit":     self.selected_unit,
            "quantity": self.ids.stepper.quantity,
        }

    def populate(self, name: str, unit: str, quantity: float,
                 locked: bool = True) -> None:
        self.ingredient_name       = name
        self.selected_unit         = unit
        self.quantity              = quantity
        self.unit_locked           = locked
        self.ids.name_field.text   = name
        self.ids.unit_spinner.text = unit
        self.ids.stepper.set_unit(unit)
        self.ids.stepper.quantity  = quantity