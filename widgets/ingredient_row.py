from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout

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

    ScrollView:
        # Above the input row on purpose: Window.softinput_mode="below_target"
        # only guarantees the focused text field clears the keyboard - anything
        # below it in the layout still gets pushed under the keyboard. Putting
        # suggestions above the field means the same pan reveals both.
        size_hint_y: None
        height: min(root.suggestion_count, 2) * dp(40)
        do_scroll_x: False

        MDBoxLayout:
            id: suggestions_box
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height

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
            on_focus: if not self.focus: root._schedule_hide_suggestions()

        MDIconButton:
            icon: "delete-outline"
            size_hint: None, None
            size: "40dp", "40dp"
            on_release: root.request_delete()
""")


class IngredientRow(MDBoxLayout):
    ingredient_name = StringProperty("")
    suggestion_count = NumericProperty(0)

    request_delete = ObjectProperty(lambda: None)
    on_name_change = ObjectProperty(None, allownone=True)

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
        self._debounce_event = Clock.schedule_once(lambda _: self._do_lookup(text), 0.3)

    def _do_lookup(self, text: str) -> None:
        from repositories.ingredient_repository import IngredientRepository

        repo = IngredientRepository()

        # Exact match → nothing more to suggest, just close the dropdown
        if repo.get_by_name(text.strip()):
            self._hide_suggestions()
            return

        results = repo.search_by_name(text)
        self._show_suggestions(results)

    def _show_suggestions(self, results: list) -> None:
        from kivymd.uix.list import OneLineListItem

        box = self.ids.suggestions_box
        box.clear_widgets()
        shown = results[:5]
        for ing in shown:
            item = OneLineListItem(
                text=ing.name.capitalize(), size_hint_y=None, height="40dp"
            )
            item.bind(on_release=lambda _, i=ing: self._apply_suggestion(i))
            box.add_widget(item)
        self.suggestion_count = len(shown)

    def _hide_suggestions(self) -> None:
        self.ids.suggestions_box.clear_widgets()
        self.suggestion_count = 0

    def _schedule_hide_suggestions(self) -> None:
        # name_field loses focus the instant a suggestion item is touched
        # (touch-down), before that item's on_release (touch-up) fires.
        # Hiding immediately here would clear the item out from under the
        # tap. Delaying gives a genuine tap-and-release time to land first;
        # a real "tap elsewhere" still hides quickly enough to feel instant.
        Clock.schedule_once(lambda _dt: self._hide_suggestions(), 0.2)

    def _apply_suggestion(self, ingredient) -> None:
        self._hide_suggestions()
        self.ingredient_name = ingredient.name
        self.ids.name_field.text = ingredient.name

    def get_data(self) -> dict:
        return {"name": self.ingredient_name.strip()}

    def populate(self, name: str) -> None:
        self.ingredient_name = name
        self.ids.name_field.text = name
