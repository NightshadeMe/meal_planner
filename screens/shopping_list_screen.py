from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from services.shopping_service import shopping_service
from constants import UNIT_LIST, UNITS
from utils import snackbar

Builder.load_string("""
<ShoppingListScreen>:
    name: "shopping_list"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: toolbar
            title: "Shopping List"
            elevation: 2
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items:
                [
                ["plus",  lambda x: root.show_add_custom_dialog()],
                ["broom", lambda x: root.confirm_clear_purchased()],
                ]

        ScrollView:
            MDBoxLayout:
                id: items_container
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "8dp"
                spacing: "4dp"
""")

Builder.load_string("""
<AddCustomItemContent>:
    orientation: "vertical"
    size_hint_y: None
    height: "272dp"
    padding: "8dp"
    spacing: "8dp"

    MDTextField:
        id: name_field
        hint_text: "Ingredient name *"
        mode: "rectangle"
        size_hint_y: None
        height: "48dp"
        on_text: root._on_name_text(self.text)

    ScrollView:
        size_hint_y: None
        height: "160dp"

        MDBoxLayout:
            id: suggestions_box
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height

    MDBoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: "8dp"

        MDRaisedButton:
            id: unit_btn
            text: root.unit
            size_hint: None, None
            size: "80dp", "44dp"
            disabled: root.unit_locked
            on_release: root.open_unit_menu()

        QuantityStepper:
            id: stepper
            unit: root.unit
            quantity: root.qty
""")


class AddCustomItemContent(MDBoxLayout):
    unit        = "g"
    qty         = UNITS["g"]["min"]
    unit_locked = False
    _menu       = None
    _debounce   = None

    def _on_name_text(self, text: str) -> None:
        if self._debounce:
            self._debounce.cancel()
        if len(text) < 2:
            self._hide_suggestions()
            return
        self._debounce = Clock.schedule_once(lambda _: self._do_lookup(text), 0.3)

    def _do_lookup(self, text: str) -> None:
        from repositories.ingredient_repository import IngredientRepository
        repo  = IngredientRepository()
        exact = repo.get_by_name(text.strip())
        if exact:
            self._hide_suggestions()
            self._apply_suggestion(exact)
            return
        self._show_suggestions(repo.search_by_name(text))

    def _show_suggestions(self, results: list) -> None:
        from kivymd.uix.list import OneLineListItem
        box = self.ids.suggestions_box
        box.clear_widgets()
        for ing in results[:4]:
            item = OneLineListItem(
                text=f"{ing.name.capitalize()}  ({ing.unit})",
                size_hint_y=None,
                height="40dp",
            )
            item.bind(on_release=lambda _, i=ing: self._apply_suggestion(i))
            box.add_widget(item)

    def _hide_suggestions(self) -> None:
        self.ids.suggestions_box.clear_widgets()

    def _apply_suggestion(self, ingredient) -> None:
        self._hide_suggestions()
        self.unit                  = ingredient.unit
        self.unit_locked           = True
        self.ids.name_field.text   = ingredient.name.capitalize()
        self.ids.unit_btn.text     = ingredient.unit
        self.ids.unit_btn.disabled = True
        self.ids.stepper.set_unit(ingredient.unit)

    def open_unit_menu(self) -> None:
        items = [
            {
                "text":       u,
                "viewclass":  "OneLineListItem",
                "on_release": (lambda u=u: self._set_unit(u)),
            }
            for u in UNIT_LIST
        ]
        self._menu = MDDropdownMenu(
            caller=self.ids.unit_btn,
            items=items,
            width="120dp",
        )
        self._menu.open()

    def _set_unit(self, unit: str) -> None:
        if self._menu:
            self._menu.dismiss()
        self.unit              = unit
        self.ids.unit_btn.text = unit
        self.ids.stepper.set_unit(unit)

    def get_data(self) -> dict | None:
        name = self.ids.name_field.text.strip()
        if not name:
            return None
        return {
            "name":     name.lower(),
            "unit":     self.unit,
            "quantity": self.ids.stepper.quantity,
        }


class ShoppingListScreen(MDScreen):
    list_id = NumericProperty(0)

    def prepare(self, list_id: int) -> None:
        self.list_id = list_id
        Clock.schedule_once(self._populate)

    def _populate(self, *_) -> None:
        sl = shopping_service.get_list_by_id(self.list_id)
        if not sl:
            self.go_back()
            return
        self.ids.toolbar.title = sl.name
        self._render_items()

    def _render_items(self) -> None:
        from widgets.shopping_item_row import ShoppingItemRow
        container = self.ids.items_container
        container.clear_widgets()

        items = shopping_service.get_items(self.list_id)
        if not items:
            from kivymd.uix.label import MDLabel
            container.add_widget(MDLabel(
                text="No items. Tap + to add custom items.",
                halign="center",
                theme_text_color="Hint",
                size_hint_y=None,
                height="48dp",
            ))
            return

        for item in items:
            row = ShoppingItemRow(
                item_id         = item.id,
                ingredient_name = item.ingredient_name.capitalize(),
                unit            = item.unit,
                quantity        = item.quantity,
                is_purchased    = item.is_purchased,
            )

            def _make_delete(item_id):
                def _delete():
                    shopping_service.delete_item(item_id)
                    self._render_items()
                return _delete

            row.request_delete = _make_delete(item.id)
            row.on_qty_changed = self._on_qty_changed
            row.on_purchased   = self._on_purchased
            container.add_widget(row)

    def _on_qty_changed(self, item_id: int, qty: float) -> None:
        shopping_service.update_quantity(item_id, qty)

    def _on_purchased(self, item_id: int, purchased: bool) -> None:
        shopping_service.toggle_purchased(item_id, purchased)
        Clock.schedule_once(lambda _: self._render_items(), 0.3)

    def show_add_custom_dialog(self) -> None:
        content = AddCustomItemContent()
        dialog  = MDDialog(
            title="Add Item",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="Add",  on_release=lambda x: self._add_custom(dialog, content)),
            ],
        )
        dialog.open()

    def _add_custom(self, dialog, content: AddCustomItemContent) -> None:
        data = content.get_data()
        if not data:
            snackbar("Enter an ingredient name")
            return
        shopping_service.add_custom_item(
            self.list_id, data["name"], data["unit"], data["quantity"]
        )
        dialog.dismiss()
        self._render_items()

    def confirm_clear_purchased(self) -> None:
        dialog = MDDialog(
            title="Clear purchased?",
            text="All ticked items will be removed from the list.",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(
                    text="Clear",
                    theme_text_color="Custom",
                    text_color=(0.8, 0.1, 0.1, 1),
                    on_release=lambda x: self._do_clear(dialog),
                ),
            ],
        )
        dialog.open()

    def _do_clear(self, dialog) -> None:
        dialog.dismiss()
        shopping_service.clear_purchased(self.list_id)
        self._render_items()

    def go_back(self) -> None:
        from kivymd.app import MDApp
        MDApp.get_running_app().navigate_to("lists")