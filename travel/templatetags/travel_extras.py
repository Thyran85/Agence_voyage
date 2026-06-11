"""Custom template tags and filters for the travel app."""
import re
from datetime import date, datetime

from django import template

register = template.Library()


def _format(value):
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


@register.filter(name="short_date")
def short_date(value):
    return _format(value)


# --------------------------------------------------------------------- #
# Destination images
# --------------------------------------------------------------------- #
_SLUG_RE = re.compile(r"[^a-z0-9]+")

# Mapping pays -> stock image. Keys are normalized (lowercased, no accents).
# Add new countries here when you drop a new file in
# static/travel/img/destinations/{slug}.jpg
_STOCK_IMAGES = {
    "madagascar": "antananarivo.jpg",
    "antananarivo": "antananarivo.jpg",
    "nosybe": "nosybe.jpg",
    "toliara": "toliara.jpg",
    "ilesaintemarie": "sainte-marie.jpg",
}

_DEFAULT_IMAGE = "default.jpg"


def _slugify(text):
    text = (text or "").lower()
    # Strip common diacritics so "espagne" stays "espagne" (we want plain ASCII)
    normalized = (
        text.replace("é", "e").replace("è", "e").replace("ê", "e")
            .replace("à", "a").replace("â", "a")
            .replace("î", "i").replace("ï", "i")
            .replace("ô", "o").replace("ö", "o")
            .replace("ù", "u").replace("û", "u")
            .replace("ç", "c")
    )
    return _SLUG_RE.sub("", normalized)


@register.filter(name="destination_image")
def destination_image(value):
    """Return a usable image URL for a destination dict.

    Resolution order:
    1. If ``image_path`` is a full URL (http/https) or starts with ``/``,
       return it as-is.
    2. Otherwise, return the stock image for the destination's pays.
    3. Fallback to a generic travel image.
    """
    if isinstance(value, dict):
        image_path = (value.get("image_path") or "").strip()
        ville = (value.get("ville") or "").strip()
        pays = (value.get("pays") or "").strip()
    else:
        image_path = (value or "").strip()
        ville = ""
        pays = ""

    if image_path:
        lowered = image_path.lower()
        if lowered.startswith(("http://", "https://", "/static/", "/media/")):
            return image_path
        return f"/static/travel/img/destinations/{image_path.lstrip('/')}"

    filename = (
        _STOCK_IMAGES.get(_slugify(ville))
        or _STOCK_IMAGES.get(_slugify(pays))
        or _DEFAULT_IMAGE
    )
    return f"/static/travel/img/destinations/{filename}"


@register.filter(name="destination_label")
def destination_label(value):
    """Return a short "Ville, Pays" label for a destination dict."""
    if not isinstance(value, dict):
        return ""
    ville = (value.get("ville") or "").strip()
    pays = (value.get("pays") or "").strip()
    if ville and pays:
        return f"{ville}, {pays}"
    return ville or pays or "—"
