"""Template context processors for the travel app."""
import logging

from django.urls import NoReverseMatch, reverse

logger = logging.getLogger(__name__)


NAV_ITEMS = (
    ("dashboard", "Tableau de bord", "layout-dashboard"),
    ("client_list", "Clients", "users"),
    ("destination_list", "Destinations", "map-pin"),
    ("voyage_list", "Voyages", "plane"),
    ("reservation_list", "Réservations", "calendar-check"),
    ("filters", "Filtres", "sliders-horizontal"),
)


def nav_items(request):
    items = []
    for name, label, icon in NAV_ITEMS:
        try:
            url = reverse(f"travel:{name}")
        except NoReverseMatch:
            logger.warning("No reverse match for nav item: %s", name)
            continue
        items.append({"name": name, "label": label, "icon": icon, "url": url})
    return {"nav_items": items}
