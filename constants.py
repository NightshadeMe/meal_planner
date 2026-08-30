import os

APP_NAME  = "MealPlanner"
DB_NAME   = "mealplanner.db"
QR_FORMAT = "mp-v1"

UNITS: dict[str, dict] = {
    "g":     {"step": 50,  "min": 50},
    "ml":    {"step": 50,  "min": 50},
    "pcs":   {"step": 1,   "min": 1},
    "tsp":   {"step": 1,   "min": 1},
    "tbsp":  {"step": 1,   "min": 1},
    "cup":   {"step": 1,   "min": 1},
    "pinch": {"step": 1,   "min": 1},
    "slice": {"step": 1,   "min": 1},
    "clove": {"step": 1,   "min": 1},
}

UNIT_LIST: list[str] = list(UNITS.keys())
MAIN_SCREENS = {"meals", "lists", "scan", "plan"}

CATEGORIES: list[str] = ["lunch", "dinner", "snack"]
CATEGORY_LABELS: dict[str, str] = {
    "lunch":  "Lunch",
    "dinner": "Dinner",
    "snack":  "Snack",
}

DAYS: list[str] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_LABELS: dict[str, str] = {
    "mon": "Monday",
    "tue": "Tuesday",
    "wed": "Wednesday",
    "thu": "Thursday",
    "fri": "Friday",
    "sat": "Saturday",
    "sun": "Sunday",
}


def get_db_path() -> str:
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, "user_data_dir"):
            return os.path.join(app.user_data_dir, DB_NAME)
    except Exception:
        pass
    return DB_NAME


def format_quantity(qty: float, unit: str) -> str:
    val = int(qty) if qty == int(qty) else qty
    return f"{val} {unit}"