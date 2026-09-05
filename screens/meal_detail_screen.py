from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from services.meal_service import meal_service
from constants import CATEGORY_LABELS
from utils import snackbar

Builder.load_string("""
<MealDetailScreen>:
    name: "meal_detail"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: toolbar
            title: "Meal"
            elevation: 2
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items:
                [
                ["pencil-outline", lambda x: root.go_edit()],
                ["qrcode",         lambda x: root.show_qr()],
                ["delete-outline", lambda x: root.confirm_delete()],
                ]

        ScrollView:
            MDBoxLayout:
                id: content
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "16dp"
                spacing: "8dp"

                MDLabel:
                    id: categories_label
                    text: ""
                    font_style: "Caption"
                    theme_text_color: "Primary"
                    size_hint_y: None
                    height: "24dp"

                MDLabel:
                    id: desc_label
                    text: ""
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    height: self.texture_size[1] + 8

                MDLabel:
                    text: "Ingredients"
                    font_style: "Subtitle1"
                    size_hint_y: None
                    height: "36dp"

                MDBoxLayout:
                    id: ingredients_list
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: "4dp"
""")


class MealDetailScreen(MDScreen):
    _meal_id: int | None = None

    def prepare(self, meal_id: int) -> None:
        self._meal_id = meal_id
        Clock.schedule_once(self._populate)

    def _populate(self, *_) -> None:
        meal = meal_service.get_by_id(self._meal_id)
        if not meal:
            self.go_back()
            return

        self.ids.toolbar.title       = meal.name
        cats = meal_service.categories_of(meal)
        self.ids.categories_label.text = " • ".join(CATEGORY_LABELS[c] for c in cats)
        self.ids.desc_label.text = meal.description or ""

        container = self.ids.ingredients_list
        container.clear_widgets()

        for mi in meal_service.get_ingredients(self._meal_id):
            from kivymd.uix.list import OneLineListItem
            container.add_widget(
                OneLineListItem(text=f"  {mi.ingredient.name.capitalize()}")
            )

    def show_qr(self) -> None:
        try:
            import qrcode
            from io import BytesIO
            from kivy.core.image import Image as CoreImage
        except ImportError:
            snackbar("qrcode / Pillow not installed")
            return

        payload = meal_service.to_qr_payload(self._meal_id)
        qr = qrcode.QRCode(
            version=None,
            box_size=8,
            border=4,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        pil_img = qr.make_image(fill_color="black", back_color="white")

        buf = BytesIO()
        pil_img.save(buf, format="PNG")
        buf.seek(0)
        texture = CoreImage(buf, ext="png").texture

        from widgets.qr_widget import QRWidget
        meal      = meal_service.get_by_id(self._meal_id)
        qr_widget = QRWidget(meal_name=meal.name)
        Clock.schedule_once(lambda _: qr_widget.set_texture(texture))

        dialog = MDDialog(
            type="custom",
            content_cls=qr_widget,
            buttons=[MDFlatButton(text="Close", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

    def go_edit(self) -> None:
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.sm.get_screen("meal_edit").prepare(meal_id=self._meal_id)
        app.navigate_to("meal_edit")

    def confirm_delete(self) -> None:
        meal   = meal_service.get_by_id(self._meal_id)
        dialog = MDDialog(
            title="Delete meal?",
            text=f"'{meal.name}' will be permanently removed.",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(
                    text="Delete",
                    theme_text_color="Custom",
                    text_color=(0.8, 0.1, 0.1, 1),
                    on_release=lambda x: self._do_delete(dialog),
                ),
            ],
        )
        dialog.open()

    def _do_delete(self, dialog) -> None:
        dialog.dismiss()
        meal_service.delete(self._meal_id)
        snackbar("Meal deleted")
        self.go_back()

    def go_back(self) -> None:
        from kivymd.app import MDApp
        MDApp.get_running_app().navigate_to("meals")