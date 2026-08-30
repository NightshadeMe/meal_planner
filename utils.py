def snackbar(text: str) -> None:
    from kivymd.uix.snackbar import MDSnackbar
    from kivymd.uix.label import MDLabel
    MDSnackbar(MDLabel(text=text)).open()