from kivy.lang import Builder
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from services.meal_service import meal_service
from services.import_service import import_service
from utils import snackbar

Builder.load_string("""
<ScanScreen>:
    name: "scan"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Scan Meal QR"
            elevation: 2

        MDBoxLayout:
            id: camera_container
            orientation: "vertical"
            size_hint: 1, 1

        MDLabel:
            id: hint_label
            text: "Point the camera at a Meal Planner QR code"
            halign: "center"
            theme_text_color: "Hint"
            size_hint_y: None
            height: "48dp"
""")


class ScanScreen(MDScreen):
    _cam = None
    _scan_event = None
    _processing = False

    def on_enter(self, *_) -> None:
        self._processing = False
        Clock.schedule_once(self._start_camera)

    def on_leave(self, *_) -> None:
        self._stop_camera()

    def _start_camera(self, *_) -> None:
        try:
            from pyzbar.pyzbar import decode
            from kivy.uix.camera import Camera
        except ImportError as e:
            self.ids.hint_label.text = (
                "Camera or pyzbar dependencies missing.\n"
                "Ensure pyzbar and libzbar are in buildozer requirements."
            )
            return

        self.ids.camera_container.clear_widgets()

        # Initialize standard Kivy camera (play=True starts feed)
        cam = Camera(play=True, resolution=(640, 480))
        self._cam = cam
        self.ids.camera_container.add_widget(cam)

        # Schedule frame scanning ~10 times a second
        self._scan_event = Clock.schedule_interval(self._scan_frame, 0.1)

    def _stop_camera(self) -> None:
        if self._scan_event:
            self._scan_event.cancel()
            self._scan_event = None

        if self._cam:
            try:
                self._cam.play = False
                self.ids.camera_container.remove_widget(self._cam)
            except Exception:
                pass
            self._cam = None

    def _scan_frame(self, dt) -> None:
        if self._processing or not self._cam or not self._cam.texture:
            return

        try:
            from pyzbar.pyzbar import decode
            from PIL import Image

            # Extract raw image data from camera texture
            texture: Texture = self._cam.texture
            pixels = texture.pixels
            size = texture.size

            # Create PIL image for pyzbar decoding
            pil_image = Image.frombytes("RGBA", size, pixels)

            # Decode barcodes
            decoded_objs = decode(pil_image)

            if decoded_objs:
                self._processing = True
                raw = decoded_objs[0].data.decode("utf-8", errors="ignore")
                self._stop_camera()
                self._handle_payload(raw)

        except Exception as exc:
            # Silence transient frame capture errors while camera initializes
            pass

    def _handle_payload(self, raw: str) -> None:
        try:
            data = import_service.parse_qr_payload(raw)
        except ValueError as exc:
            snackbar(str(exc))
            self._restart_camera()
            return

        if meal_service.name_exists(data["name"]):
            self._show_conflict_dialog(data)
        else:
            self._do_import(data, overwrite=False)

    def _show_conflict_dialog(self, data: dict) -> None:
        dialog = MDDialog(
            title="Meal already exists",
            text=f"A meal named '{data['name']}' is already saved. What would you like to do?",
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda x: [dialog.dismiss(), self._restart_camera()],
                ),
                MDFlatButton(
                    text="Save as copy",
                    on_release=lambda x: [
                        dialog.dismiss(),
                        self._do_import(data, overwrite=False, as_copy=True),
                    ],
                ),
                MDRaisedButton(
                    text="Overwrite",
                    on_release=lambda x: [
                        dialog.dismiss(),
                        self._do_import(data, overwrite=True),
                    ],
                ),
            ],
        )
        dialog.open()

    def _do_import(self, data: dict, overwrite: bool, as_copy: bool = False) -> None:
        name = data["name"]
        desc = data["description"]
        categories = data["categories"]
        ingredients = [{"name": i["name"]} for i in data["ingredients"]]

        if overwrite:
            meals = meal_service.get_all()
            existing = next((m for m in meals if m.name == name), None)
            if existing:
                meal_service.update(existing.id, name, desc, ingredients, categories)
                snackbar(f"'{name}' updated")
            else:
                meal_service.create(name, desc, ingredients, categories)
                snackbar(f"'{name}' imported")
        elif as_copy:
            copy_name = f"{name} (copy)"
            meal_service.create(copy_name, desc, ingredients, categories)
            snackbar(f"Saved as '{copy_name}'")
        else:
            meal_service.create(name, desc, ingredients, categories)
            snackbar(f"'{name}' imported")

        from kivymd.app import MDApp

        MDApp.get_running_app().navigate_to("meals")

    def _restart_camera(self) -> None:
        self._processing = False
        Clock.schedule_once(self._start_camera, 0.5)

