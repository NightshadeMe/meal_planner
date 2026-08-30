from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from services.meal_service import meal_service
from utils import snackbar

Builder.load_string("""
<MealsScreen>:
    name: "meals"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "My Meals"
            elevation: 2

        ScrollView:
            MDList:
                id: meals_list

        MDFloatingActionButton:
            icon: "plus"
            pos_hint: {"right": .95, "y": .05}
            on_release: root.go_new_meal()
""")


def _meal_row(name: str, sublabel: str, on_tap, on_edit) -> MDBoxLayout:
    row = MDBoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(56),
        padding=(dp(16), 0),
        spacing=dp(4),
    )

    info = MDBoxLayout(orientation="vertical", size_hint_x=1)
    info.add_widget(
        MDLabel(
            text=name,
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(28),
            shorten=True,
            shorten_from="right",
        )
    )
    info.add_widget(
        MDLabel(
            text=sublabel,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
        )
    )
    row.add_widget(info)

    edit_btn = MDIconButton(
        icon="pencil-outline",
        size_hint=(None, None),
        size=(dp(40), dp(40)),
        pos_hint={"center_y": 0.5},
    )
    edit_btn.bind(on_release=lambda _: on_edit())
    row.add_widget(edit_btn)

    row.bind(
        on_touch_up=lambda inst, touch: (
            on_tap()
            if inst.collide_point(*touch.pos)
            and not edit_btn.collide_point(*touch.pos)
            else None
        )
    )
    return row


class MealsScreen(MDScreen):

    def on_enter(self, *args) -> None:
        self.refresh()

    def refresh(self) -> None:
        lst = self.ids.meals_list
        lst.clear_widgets()
        meals = meal_service.get_all()

        if not meals:
            from kivymd.uix.list import OneLineListItem

            lst.add_widget(OneLineListItem(text="No meals yet — tap + to add one"))
            return

        # Single GROUP BY query instead of one query per meal
        counts = meal_service.get_ingredient_counts([m.id for m in meals])

        for meal in meals:
            count = counts.get(meal.id, 0)
            label = f"{count} ingredient{'s' if count != 1 else ''}"
            row = _meal_row(
                name=meal.name,
                sublabel=label,
                on_tap=(lambda mid=meal.id: self.go_detail(mid)),
                on_edit=(lambda mid=meal.id: self.go_edit_meal(mid)),
            )
            lst.add_widget(row)

    def go_new_meal(self) -> None:
        from kivymd.app import MDApp

        app = MDApp.get_running_app()
        app.sm.get_screen("meal_edit").prepare(meal_id=None)
        app.navigate_to("meal_edit")

    def go_edit_meal(self, meal_id: int) -> None:
        from kivymd.app import MDApp

        app = MDApp.get_running_app()
        app.sm.get_screen("meal_edit").prepare(meal_id=meal_id)
        app.navigate_to("meal_edit")

    def go_detail(self, meal_id: int) -> None:
        from kivymd.app import MDApp

        app = MDApp.get_running_app()
        app.sm.get_screen("meal_detail").prepare(meal_id=meal_id)
        app.navigate_to("meal_detail")

    def confirm_delete(self, meal_id: int, name: str) -> None:
        dialog = MDDialog(
            title="Delete meal?",
            text=f"'{name}' will be permanently removed.",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(
                    text="Delete",
                    theme_text_color="Custom",
                    text_color=(0.8, 0.1, 0.1, 1),
                    on_release=lambda x: self._do_delete(dialog, meal_id),
                ),
            ],
        )
        dialog.open()

    def _do_delete(self, dialog, meal_id: int) -> None:
        dialog.dismiss()
        meal_service.delete(meal_id)
        snackbar("Meal deleted")
        self.refresh()
