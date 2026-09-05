import os

APP_NAME  = "MealPlanner"
DB_NAME   = "mealplanner.db"
QR_FORMAT = "mp-v2"   # v2: ingredients are name-only (no quantity/unit)

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

# Sentinel (day, category) pair for the single "Favorites" slot in the
# weekly plan. Reuses PlannedMeal's existing unique-(day, category) row
# instead of a separate table - it's just one more cell that happens not
# to belong to a real day or a lunch/dinner/snack category.
FAVORITES_DAY      = "favorites"
FAVORITES_CATEGORY = "favorites"


def get_db_path() -> str:
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, "user_data_dir"):
            return os.path.join(app.user_data_dir, DB_NAME)
    except Exception:
        pass
    return DB_NAME