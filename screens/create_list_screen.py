from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from services.meal_service import meal_service
from services.shopping_service import shopping_service
from utils import snackbar

Builder.load_string("""
<CreateListScreen>:
    name: "create_list"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "New Shopping List"
            elevation: 2
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: "16dp"
            spacing: "12dp"

            MDTextField:
                id: list_name_field
                hint_text: "List name *"
                mode: "rectangle"

            MDLabel:
                text: "Select meals to include:"
                font_style: "Subtitle1"
                size_hint_y: None
                height: "32dp"

            ScrollView:
                MDList:
                    id: meal_selection_list

            MDRaisedButton:
                text: "Generate Shopping List"
                icon: "cart-arrow-down"
                size_hint_x: 1
                size_hint_y: None
                height: "48dp"
                on_release: root.generate()
""")


class CreateListScreen(MDScreen):
    _selected: set[int]

    def on_pre_enter(self, *_) -> None:
        self._selected = set()
        self.ids.list_name_field.text = ""
        self._load_meals()

    def _load_meals(self) -> None:
        lst = self.ids.meal_selection_list
        lst.clear_widgets()
        meals = meal_service.get_all()

        if not meals:
            from kivymd.uix.list import OneLineListItem
            lst.add_widget(OneLineListItem(text="No meals saved yet."))
            return

        for meal in meals:
            count = len(meal_service.get_ingredients(meal.id))
            label = f"{count} ingredient{'s' if count != 1 else ''}"

            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(56),
                padding=(dp(8), 0),
                spacing=dp(4),
            )
            row.meal_id = meal.id

            chk_btn = MDIconButton(
                icon="checkbox-blank-outline",
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                pos_hint={"center_y": .5},
            )
            chk_btn.meal_id = meal.id
            chk_btn.bind(on_release=lambda btn: self._toggle(btn))
            row.add_widget(chk_btn)

            info = MDBoxLayout(orientation="vertical", size_hint_x=1)
            info.add_widget(MDLabel(
                text=meal.name, font_style="Subtitle1",
                size_hint_y=None, height=dp(28),
            ))
            info.add_widget(MDLabel(
                text=label, font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None, height=dp(20),
            ))
            row.add_widget(info)
            lst.add_widget(row)

    def _toggle(self, btn) -> None:
        mid = btn.meal_id
        if mid in self._selected:
            self._selected.discard(mid)
            btn.icon = "checkbox-blank-outline"
        else:
            self._selected.add(mid)
            btn.icon = "checkbox-marked"

    def generate(self) -> None:
        name = self.ids.list_name_field.text.strip()
        if not name:
            snackbar("Please enter a list name")
            return
        if not self._selected:
            snackbar("Select at least one meal")
            return

        sl = shopping_service.create_list(name, list(self._selected))
        snackbar(f"'{name}' created")

        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.sm.get_screen("shopping_list").prepare(list_id=sl.id)
        app.navigate_to("shopping_list")

    def go_back(self) -> None:
        from kivymd.app import MDApp
        MDApp.get_running_app().navigate_to("lists")