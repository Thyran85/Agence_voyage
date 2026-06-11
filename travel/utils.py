"""Utility helpers shared by travel views."""
from datetime import date, datetime


def format_date(value):
    if value is None or value == "":
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    text = str(value)
    if len(text) >= 10:
        return text[:10]
    return text


def format_price(value):
    if value is None or value == "":
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:,.0f} Ar".replace(",", " ")


def short_text(value, limit=60):
    if not value:
        return ""
    text = str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def client_label(row):
    if not row:
        return ""
    return f"{row.get('prenom', '')} {row.get('nom', '')}".strip()


def destination_label(row):
    if not row:
        return ""
    pays = row.get("pays", "")
    ville = row.get("ville", "")
    if pays and ville:
        return f"{pays} - {ville}"
    return pays or ville or ""


def voyage_label(row):
    if not row:
        return ""
    return f"Voyage #{row.get('id_voyage', '')} - {row.get('ville', '')}".strip(" -")
