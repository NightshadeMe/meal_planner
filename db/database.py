from db.models import database, ALL_MODELS


def init_db(path: str) -> None:
    """Open the SQLite file and create tables if they don't exist."""
    database.init(
        path,
        pragmas={
            "journal_mode": "wal",
            "foreign_keys": 1,
            "cache_size": -1024 * 32,   # 32 MB page cache
        },
    )
    database.connect()
    database.create_tables(ALL_MODELS, safe=True)
    _migrate_meal_category_columns()


def _migrate_meal_category_columns() -> None:
    """
    Older installs may have a 'meal' table without the is_lunch/is_dinner/
    is_snack columns. Add them if missing, and give any pre-existing meal
    a default category so it doesn't just disappear from every list.
    """
    existing_cols = {row[1] for row in database.execute_sql("PRAGMA table_info(meal)").fetchall()}
    added_any = False
    for col in ("is_lunch", "is_dinner", "is_snack"):
        if col not in existing_cols:
            database.execute_sql(f"ALTER TABLE meal ADD COLUMN {col} INTEGER NOT NULL DEFAULT 0")
            added_any = True

    if added_any:
        database.execute_sql(
            "UPDATE meal SET is_dinner = 1 "
            "WHERE is_lunch = 0 AND is_dinner = 0 AND is_snack = 0"
        )


def close_db() -> None:
    if not database.is_closed():
        database.close()
