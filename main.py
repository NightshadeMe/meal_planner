from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.app import MDApp

# Keeps the focused text field visible above the soft keyboard instead of
# letting the keyboard cover it - relevant for forms like meal editing where
# ingredient rows can push fields down the screen.
Window.softinput_mode = "below_target"

import widgets.stepper
import widgets.ingredient_row
import widgets.shopping_item_row
import widgets.bottom_nav
import widgets.qr_widget

from screens.meals_screen import MealsScreen
from screens.meal_edit_screen import MealEditScreen
from screens.meal_detail_screen import MealDetailScreen
from screens.plan_screen import PlanScreen
from screens.lists_screen import ListsScreen
from screens.create_list_screen import CreateListScreen
from screens.shopping_list_screen import ShoppingListScreen
from screens.scan_screen import ScanScreen

from db.database import init_db, close_db
from constants import get_db_path, MAIN_SCREENS

Builder.load_string("""
<RootLayout>:
    orientation: "vertical"

    ScreenManager:
        id: sm

    BottomNavBar:
        id: bottom_nav
""")

from kivymd.uix.boxlayout import MDBoxLayout


class RootLayout(MDBoxLayout):
    pass


class MealPlannerApp(MDApp):
    current_screen = StringProperty("meals")

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"

        # DB must be ready before any screen's on_enter fires
        init_db(get_db_path())

        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(MealsScreen())
        self.sm.add_widget(MealEditScreen())
        self.sm.add_widget(MealDetailScreen())
        self.sm.add_widget(PlanScreen())
        self.sm.add_widget(ListsScreen())
        self.sm.add_widget(CreateListScreen())
        self.sm.add_widget(ShoppingListScreen())
        self.sm.add_widget(ScanScreen())
        self.sm.current = "meals"

        root = RootLayout()
        root.remove_widget(root.ids.sm)
        root.add_widget(self.sm, index=1)

        return root

    def on_stop(self) -> None:
        close_db()

    def navigate_to(self, screen_name: str) -> None:
        self.sm.current = screen_name
        self.current_screen = screen_name
        try:
            nav = self.root.ids.bottom_nav
            nav.opacity = 1 if screen_name in MAIN_SCREENS else 0
            nav.disabled = screen_name not in MAIN_SCREENS
        except Exception:
            pass


if __name__ == "__main__":
    MealPlannerApp().run()
