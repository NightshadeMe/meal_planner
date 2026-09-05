from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu

Builder.load_string("""
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
""")


class IngredientRow(MDBoxLayout):
    # Suggestions render in a floating MDDropdownMenu (see _show_suggestions),
    # not as part of this row's own layout. Row height never changes based on
    # typing/suggestion state, so there's nothing here for the keyboard's
    # focus-follow scrolling or Window's softinput panning to fight over.
    ingredient_name = StringProperty("")

    request_delete = ObjectProperty(lambda: None)
    on_name_change = ObjectProperty(None, allownone=True)

    _debounce_event = None
    _menu = None

    def _on_name_text(self, text: str) -> None:
        self.ingredient_name = text
        if self.on_name_change:
            self.on_name_change(self, text)

        if self._debounce_event:
            self._debounce_event.cancel()
            self._debounce_event = None

        if len(text) < 2:
            self._hide_suggestions()
            return

        self._debounce_event = Clock.schedule_once(lambda _: self._do_lookup(text), 0.3)

    def _do_lookup(self, text: str) -> None:
        from repositories.ingredient_repository import IngredientRepository

        repo = IngredientRepository()

        if repo.get_by_name(text.strip()):
            self._hide_suggestions()
            return

        self._show_suggestions(repo.search_by_name(text))

    def _show_suggestions(self, results: list) -> None:
        self._hide_suggestions()
        if not results:
            return

        items = [
            {
                "text": ing.name.capitalize(),
                "viewclass": "OneLineListItem",
                "on_release": (lambda i=ing: self._apply_suggestion(i)),
            }
            for ing in results[:5]
        ]
        self._menu = MDDropdownMenu(
            caller=self.ids.name_field,
            items=items,
            position="top",  # always opens upward from the field, never
            # relies on Window.height (which doesn't
            # account for the on-screen keyboard)
            max_height="200dp",  # ~5 rows; scrolls internally past that
            width=self.ids.name_field.width,
        )
        self._menu.open()

    def _hide_suggestions(self) -> None:
        if self._menu:
            self._menu.dismiss()
            self._menu = None

    def _apply_suggestion(self, ingredient) -> None:
        self._hide_suggestions()
        self.ingredient_name = ingredient.name
        self.ids.name_field.text = ingredient.name

    def get_data(self) -> dict:
        return {"name": self.ingredient_name.strip()}

    def populate(self, name: str) -> None:
        self.ingredient_name = name
        self.ids.name_field.text = name
