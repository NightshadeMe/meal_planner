from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from constants import UNITS

Builder.load_string("""
<QuantityStepper>:
    orientation: "horizontal"
    size_hint_y: None
    height: "40dp"
    spacing: "2dp"
    padding: 0

    MDIconButton:
        id: btn_minus
        icon: "minus-circle-outline"
        size_hint: None, None
        size: "40dp", "40dp"
        on_release: root._decrement()

    MDLabel:
        id: qty_label
        text: root._display_text()
        halign: "center"
        size_hint_x: None
        width: "64dp"
        font_style: "Body1"

    MDIconButton:
        id: btn_plus
        icon: "plus-circle-outline"
        size_hint: None, None
        size: "40dp", "40dp"
        on_release: root._increment()
""")


class QuantityStepper(MDBoxLayout):
    quantity  = NumericProperty(0)
    unit      = StringProperty("g")
    on_change = ObjectProperty(None, allownone=True)

    def _cfg(self) -> dict:
        return UNITS.get(self.unit, {"step": 1, "min": 1})

    def _display_text(self) -> str:
        qty = self.quantity
        val = int(qty) if qty == int(qty) else round(qty, 2)
        return f"{val}"

    def _increment(self) -> None:
        self.quantity += self._cfg()["step"]
        self._notify()

    def _decrement(self) -> None:
        cfg     = self._cfg()
        new_qty = self.quantity - cfg["step"]
        if new_qty >= cfg["min"]:
            self.quantity = new_qty
            self._notify()

    def _notify(self) -> None:
        if self.on_change:
            self.on_change(self.quantity)

    def set_unit(self, unit: str) -> None:
        """Switch unit and reset quantity to the new unit's minimum."""
        self.unit     = unit
        self.quantity = self._cfg()["min"]

    def on_quantity(self, _instance, _value) -> None:
        if self.ids:
            self.ids.qty_label.text = self._display_text()