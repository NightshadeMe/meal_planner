from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.textfield import MDTextField

from services.meal_service import meal_service
from services.plan_service import plan_service
from constants import DAYS, DAY_LABELS, CATEGORY_LABELS, FAVORITES_DAY, FAVORITES_CATEGORY
from utils import snackbar

# Column order for this screen only (meal editing / meal list keep the
# lunch/dinner/snack order defined in constants.CATEGORIES).
PLANNER_COLUMNS = ["lunch", "snack", "dinner"]

Builder.load_string("""
<PlanCell>:
    canvas.before:
        Color:
            rgba: 0.93, 0.93, 0.93, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [6]

<PlanScreen>:
    name: "plan"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Weekly Plan"
            elevation: 2
            right_action_items: [["cart-arrow-down", lambda x: root.generate_list()]]

        ScrollView:
            MDBoxLayout:
                id: grid_container
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "8dp"
                spacing: "4dp"
""")


class PlanCell(MDBoxLayout):
    pass


class PlanScreen(MDScreen):
    _dialog = None
    _name_field = None

    def on_enter(self, *_args) -> None:
        self.refresh()

    def refresh(self) -> None:
        container = self.ids.grid_container
        container.clear_widgets()
        grid = plan_service.get_grid()

        header = MDBoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(32), spacing=dp(4)
        )
        header.add_widget(MDLabel(text="", size_hint_x=0.22))
        for cat in PLANNER_COLUMNS:
            header.add_widget(
                MDLabel(
                    text=CATEGORY_LABELS[cat],
                    font_style="Caption",
                    halign="center",
                    size_hint_x=0.26,
                )
            )
        container.add_widget(header)

        for day in DAYS:
            row = MDBoxLayout(
                orientation="horizontal", size_hint_y=None, height=dp(56), spacing=dp(4)
            )
            row.add_widget(MDLabel(text=DAY_LABELS[day][:3], size_hint_x=0.22))
            for cat in PLANNER_COLUMNS:
                meal = grid.get((day, cat))
                row.add_widget(self._cell(day, cat, meal))
            container.add_widget(row)

        # Single extra slot, not tied to any day - e.g. a "Staples" meal
        # covering whatever you buy every week regardless of what's cooked.
        fav_row = MDBoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(56), spacing=dp(4)
        )
        fav_row.add_widget(MDLabel(text="Favorites", size_hint_x=0.22))
        fav_meal = grid.get((FAVORITES_DAY, FAVORITES_CATEGORY))
        fav_row.add_widget(
            self._cell(FAVORITES_DAY, FAVORITES_CATEGORY, fav_meal, size_hint_x=0.78)
        )
        container.add_widget(fav_row)

    def _cell(self, day: str, category: str, meal, size_hint_x: float = 0.26) -> PlanCell:
        cell = PlanCell(
            size_hint_x=size_hint_x,
            size_hint_y=None,
            height=dp(48),
            padding=(dp(4), 0),
        )
        label = MDLabel(
            text=(meal.name if meal else "+"),
            halign="center",
            valign="middle",
            shorten=True,
            shorten_from="right",
            theme_text_color="Primary" if meal else "Hint",
        )
        label.bind(size=label.setter("text_size"))
        cell.add_widget(label)
        cell.bind(
            on_touch_up=lambda inst, touch: (
                self.open_picker(day, category)
                if inst.collide_point(*touch.pos)
                else None
            )
        )
        return cell

    # ------------------------------------------------------------ picker --

    def open_picker(self, day: str, category: str) -> None:
        is_favorites = day == FAVORITES_DAY
        if is_favorites:
            meals = meal_service.get_all()
            title = "Favorites"
            empty_text = "No meals saved yet"
        else:
            meals = meal_service.get_by_category(category)
            title = f"{DAY_LABELS[day]} • {CATEGORY_LABELS[category]}"
            empty_text = f"No {CATEGORY_LABELS[category].lower()} meals yet"

        mlist = MDList()
        mlist.add_widget(
            OneLineListItem(
                text="Clear this slot",
                on_release=lambda _i: self._apply_pick(day, category, None),
            )
        )
        if not meals:
            mlist.add_widget(OneLineListItem(text=empty_text, disabled=True))
        for meal in meals:
            mlist.add_widget(
                OneLineListItem(
                    text=meal.name,
                    on_release=lambda _i, mid=meal.id: self._apply_pick(
                        day, category, mid
                    ),
                )
            )

        content = ScrollView(size_hint_y=None, height=dp(300))
        content.add_widget(mlist)

        self._dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: self._dialog.dismiss())
            ],
        )
        self._dialog.open()

    def _apply_pick(self, day: str, category: str, meal_id: int | None) -> None:
        self._dialog.dismiss()
        if meal_id is None:
            plan_service.clear_meal(day, category)
        else:
            plan_service.set_meal(day, category, meal_id)
        self.refresh()

    # ------------------------------------------------------- shopping list --

    def generate_list(self) -> None:
        if not plan_service.get_grid():
            snackbar("Plan at least one meal first")
            return

        self._name_field = MDTextField(hint_text="List name", text="Week Plan")
        self._dialog = MDDialog(
            title="Generate Shopping List",
            type="custom",
            content_cls=self._name_field,
            buttons=[
                MDFlatButton(
                    text="Cancel", on_release=lambda x: self._dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Generate", on_release=lambda x: self._do_generate()
                ),
            ],
        )
        self._dialog.open()

    def _do_generate(self) -> None:
        name = self._name_field.text.strip() or "Week Plan"
        self._dialog.dismiss()

        sl = plan_service.generate_shopping_list(name)
        snackbar(f"'{sl.name}' created")

        from kivymd.app import MDApp

        app = MDApp.get_running_app()
        app.sm.get_screen("shopping_list").prepare(list_id=sl.id)
        app.navigate_to("shopping_list")