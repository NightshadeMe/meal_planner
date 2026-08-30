from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from services.shopping_service import shopping_service
from utils import snackbar

Builder.load_string("""
<ListsScreen>:
    name: "lists"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Shopping Lists"
            elevation: 2

        ScrollView:
            MDList:
                id: lists_list

        MDFloatingActionButton:
            icon: "plus"
            pos_hint: {"right": .95, "y": .05}
            on_release: root.go_create()
""")


def _list_row(name: str, sublabel: str, on_tap, on_delete) -> MDBoxLayout:
    row = MDBoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(56),
        padding=(dp(16), 0),
        spacing=dp(4),
    )

    info = MDBoxLayout(orientation="vertical", size_hint_x=1)
    info.add_widget(MDLabel(
        text=name, font_style="Subtitle1",
        size_hint_y=None, height=dp(28), shorten=True, shorten_from="right",
    ))
    info.add_widget(MDLabel(
        text=sublabel, font_style="Caption",
        theme_text_color="Secondary",
        size_hint_y=None, height=dp(20),
    ))
    row.add_widget(info)

    del_btn = MDIconButton(icon="delete-outline", size_hint=(None, None),
                           size=(dp(40), dp(40)), pos_hint={"center_y": .5})
    del_btn.bind(on_release=lambda _: on_delete())
    row.add_widget(del_btn)

    row.bind(on_touch_up=lambda inst, touch:
             on_tap() if inst.collide_point(*touch.pos) and not del_btn.collide_point(*touch.pos) else None)
    return row


class ListsScreen(MDScreen):

    def on_enter(self, *_) -> None:
        self.refresh()

    def refresh(self) -> None:
        lst = self.ids.lists_list
        lst.clear_widgets()
        lists = shopping_service.get_all_lists()

        if not lists:
            from kivymd.uix.list import OneLineListItem
            lst.add_widget(OneLineListItem(text="No lists yet — tap + to create one"))
            return

        for sl in lists:
            count = shopping_service.item_count(sl.id)
            label = f"{count} item{'s' if count != 1 else ''}  •  {sl.created_at.strftime('%d %b %Y')}"
            row   = _list_row(
                name      = sl.name,
                sublabel  = label,
                on_tap    = (lambda lid=sl.id: self.go_list(lid)),
                on_delete = (lambda lid=sl.id, lname=sl.name: self.confirm_delete(lid, lname)),
            )
            lst.add_widget(row)

    def go_create(self) -> None:
        from kivymd.app import MDApp
        MDApp.get_running_app().navigate_to("create_list")

    def go_list(self, list_id: int) -> None:
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.sm.get_screen("shopping_list").prepare(list_id=list_id)
        app.navigate_to("shopping_list")

    def confirm_delete(self, list_id: int, name: str) -> None:
        dialog = MDDialog(
            title="Delete list?",
            text=f"'{name}' and all its items will be removed.",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(
                    text="Delete",
                    theme_text_color="Custom",
                    text_color=(0.8, 0.1, 0.1, 1),
                    on_release=lambda x: self._do_delete(dialog, list_id),
                ),
            ],
        )
        dialog.open()

    def _do_delete(self, dialog, list_id: int) -> None:
        dialog.dismiss()
        shopping_service.delete_list(list_id)
        snackbar("List deleted")
        self.refresh()