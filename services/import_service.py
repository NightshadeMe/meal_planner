import json
from constants import QR_FORMAT, UNIT_LIST, CATEGORIES


class ImportService:

    def parse_qr_payload(self, raw: str) -> dict:
        """
        Parse and validate a raw QR string.
        Returns a normalised dict::

            {
                "name": str,
                "description": str,
                "ingredients": [{"name": str, "qty": float, "unit": str}, ...]
            }

        Raises ``ValueError`` with a human-readable message on any problem.
        """
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError as exc:
            raise ValueError(f"Not a valid QR code: {exc}") from exc

        if data.get("fmt") != QR_FORMAT:
            raise ValueError(
                f"Unknown format '{data.get('fmt')}'. "
                f"Expected '{QR_FORMAT}'."
            )

        name = (data.get("name") or "").strip()
        if not name:
            raise ValueError("QR payload is missing a meal name.")

        raw_ingredients = data.get("ing", [])
        ingredients: list[dict] = []
        for ing in raw_ingredients:
            ing_name = (ing.get("n") or "").strip()
            ing_unit = (ing.get("u") or "").strip()
            if not ing_name or ing_unit not in UNIT_LIST:
                continue   # skip malformed entries silently
            ingredients.append({
                "name": ing_name,
                "qty":  float(ing.get("q", 1)),
                "unit": ing_unit,
            })

        raw_categories = data.get("cat", [])
        categories = [c for c in raw_categories if c in CATEGORIES] \
            if isinstance(raw_categories, list) else []
        if not categories:
            categories = ["dinner"]   # older QR codes predate categories

        return {
            "name":        name,
            "description": (data.get("desc") or "").strip(),
            "ingredients": ingredients,
            "categories":  categories,
        }


import_service = ImportService()
