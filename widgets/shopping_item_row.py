from kivy.lang import Builder
from kivy.properties import (
    NumericProperty, StringProperty,
    BooleanProperty, ObjectProperty,
)
from kivymd.uix.boxlayout import MDBoxLayout

Builder.load_string("""
<ShoppingItemRow>:
    orientation: "horizontal"
    size_hint_y: None
    height: "56dp"
    padding: "8dp", "4dp"
    spacing: "8dp"

    canvas.before:
        Color:
            rgba: (0.85, 0.85, 0.85, 1) if root.is_purchased else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [6]

    MDCheckbox:
        id: chk
        size_hint: None, None
        size: "40dp", "40dp"
        active: root.is_purchased
        on_active: root._on_toggle(self.active)

    MDLabel:
        id: name_lbl
        text: ("[s]" + root.ingredient_name + "[/s]") if root.is_purchased else root.ingredient_name
        markup: True
        size_hint_x: 1
        font_style: "Body1"
        theme_text_color: "Secondary" if root.is_purchased else "Primary"
        valign: "center"
        shorten: True
        shorten_from: "right"

    QuantityStepper:
        id: stepper
        quantity: root.quantity
        size_hint_x: None
        width: "148dp"

    MDIconButton:
        icon: "delete-outline"
        size_hint: None, None
        size: "40dp", "40dp"
        on_release: root.request_delete()
""")


class ShoppingItemRow(MDBoxLayout):
    item_id         = NumericProperty(0)
    ingredient_name = StringProperty("")
    quantity        = NumericProperty(1)
    is_purchased    = BooleanProperty(False)

    request_delete  = ObjectProperty(lambda: None)
    on_qty_changed  = ObjectProperty(None, allownone=True)
    on_purchased    = ObjectProperty(None, allownone=True)

    def on_kv_post(self, base_widget) -> None:
        # Wire stepper quantity changes in Python — KV on_change: won't work
        # because 'change' is not a registered Kivy event name.
        self.ids.stepper.bind(quantity=self._stepper_quantity_changed)

    def _stepper_quantity_changed(self, _instance, value: float) -> None:
        self.quantity = value
        if self.on_qty_changed:
            self.on_qty_changed(self.item_id, value)

    def _on_toggle(self, active: bool) -> None:
        self.is_purchased = active
        if self.on_purchased:
            self.on_purchased(self.item_id, active)