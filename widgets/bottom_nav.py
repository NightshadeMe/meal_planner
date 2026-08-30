from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout

Builder.load_string("""
<NavButton>:
    orientation: "vertical"
    size_hint_x: 1
    spacing: 0
    padding: 0

    MDIconButton:
        icon: root.icon
        size_hint: None, None
        size: "48dp", "36dp"
        pos_hint: {"center_x": .5}
        theme_icon_color: "Custom"
        icon_color: app.theme_cls.primary_color if root.active else app.theme_cls.disabled_hint_text_color
        on_release: app.navigate_to(root.target)

    MDLabel:
        text: root.label
        font_style: "Caption"
        halign: "center"
        theme_text_color: "Custom"
        text_color: app.theme_cls.primary_color if root.active else app.theme_cls.disabled_hint_text_color
        size_hint_y: None
        height: "16dp"


<BottomNavBar>:
    size_hint_y: None
    height: "56dp"
    orientation: "horizontal"
    padding: "8dp", "4dp"
    spacing: 0

    canvas.before:
        Color:
            rgba: app.theme_cls.bg_normal
        Rectangle:
            pos: self.pos
            size: self.size

    NavButton:
        icon: "silverware-fork-knife"
        label: "Meals"
        target: "meals"
        active: app.current_screen == "meals"

    NavButton:
        icon: "calendar-week"
        label: "Plan"
        target: "plan"
        active: app.current_screen == "plan"

    NavButton:
        icon: "cart-outline"
        label: "Shopping"
        target: "lists"
        active: app.current_screen == "lists"

    NavButton:
        icon: "qrcode-scan"
        label: "Scan"
        target: "scan"
        active: app.current_screen == "scan"
""")


class NavButton(MDBoxLayout):
    icon   = StringProperty("")
    label  = StringProperty("")
    target = StringProperty("")
    active = BooleanProperty(False)


class BottomNavBar(MDBoxLayout):
    pass