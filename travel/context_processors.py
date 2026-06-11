"""Template context processors for the travel app."""
from django.urls import NoReverseMatch, reverse


NAV_ITEMS = (
    ("dashboard", "Tableau de bord", "layout-dashboard"),
    ("client_list", "Clients", "users"),
    ("destination_list", "Destinations", "map-pin"),
    ("voyage_list", "Voyages", "plane"),
    ("reservation_list", "Réservations", "calendar-check"),
    ("filters", "Filtres", "sliders-horizontal"),
    ("sql_examples", "SQL Oracle", "database"),
)


def nav_items(request):
    items = []
    for name, label, icon in NAV_ITEMS:
        try:
            url = reverse(f"travel:{name}")
        except NoReverseMatch:
            continue
        items.append({"name": name, "label": label, "icon": icon, "url": url})
    return {"nav_items": items}
