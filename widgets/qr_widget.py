from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

Builder.load_string("""
<QRWidget>:
    orientation: "vertical"
    size_hint_y: None
    height: "320dp"
    padding: "16dp"
    spacing: "8dp"

    MDLabel:
        text: root.meal_name
        font_style: "H6"
        halign: "center"
        size_hint_y: None
        height: "32dp"

    Image:
        id: qr_image
        size_hint: 1, 1
        allow_stretch: True
        keep_ratio: True
""")


class QRWidget(MDBoxLayout):
    meal_name = StringProperty("")

    def set_texture(self, texture) -> None:
        self.ids.qr_image.texture = texture
