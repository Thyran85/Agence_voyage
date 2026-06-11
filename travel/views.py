"""Views for the travel app."""
import csv
import json
import uuid
from datetime import date
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from app.services.query_examples import QUERY_EXAMPLES
from travel.forms import (
    ClientForm,
    DestinationForm,
    FilterReservationForm,
    FilterVoyageForm,
    ReservationForm,
    VoyageForm,
)
from travel.services import get_service
from travel.utils import format_date


NAV_LABELS = {
    "dashboard": "Tableau de bord",
    "client_list": "Clients",
    "destination_list": "Destinations",
    "voyage_list": "Voyages",
    "reservation_list": "Réservations",
    "filters": "Filtres",
    "sql_examples": "SQL Oracle",
}


def _resolve_view_name(request):
    match = request.resolver_match
    return match.view_name.split(":")[-1] if match else ""


def _base_context(request, **extra):
    view_name = _resolve_view_name(request)
    return {
        "active_nav": view_name,
        "page_title": NAV_LABELS.get(view_name, ""),
        **extra,
    }


_STOCK_IMAGE_MAP = {
    "france": "/static/travel/img/destinations/paris.jpg",
    "italie": "/static/travel/img/destinations/rome.jpg",
    "italy": "/static/travel/img/destinations/rome.jpg",
    "espagne": "/static/travel/img/destinations/barcelone.jpg",
    "spain": "/static/travel/img/destinations/barcelone.jpg",
    "maroc": "/static/travel/img/destinations/marrakech.jpg",
    "morocco": "/static/travel/img/destinations/marrakech.jpg",
}


def _destination_form_context(request, **extra):
    return _base_context(
        request,
        stock_images=json.dumps(_STOCK_IMAGE_MAP),
        **extra,
    )


def _split_search(search_by, search_value, sort_by, sort_dir, default_sort):
    return {
        "search_by": search_by or None,
        "search_value": (search_value or "").strip() or None,
        "sort_by": sort_by or default_sort,
        "sort_dir": sort_dir or "ASC",
    }


# --------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------- #
def dashboard(request):
    service = get_service()
    try:
        stats = service.dashboard_stats()
        recent = service.recent_reservations(limit=4)
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Erreur Oracle : {exc}")
        stats = {
            "clients": 0,
            "destinations": 0,
            "voyages": 0,
            "reservations": 0,
            "destination_top": None,
            "voyage_top": None,
        }
        recent = []

    return render(
        request,
        "travel/dashboard.html",
        _base_context(
            request,
            stats=stats,
            recent=recent,
        ),
    )


# --------------------------------------------------------------------- #
# Clients
# --------------------------------------------------------------------- #
def client_list(request):
    service = get_service()
    search_by = request.GET.get("search_by")
    search_value = request.GET.get("search_value")
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir", "ASC")
    try:
        clients = service.clients.list(**_split_search(search_by, search_value, sort_by, sort_dir, "nom"))
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Erreur Oracle : {exc}")
        clients = []
    return render(
        request,
        "travel/client_list.html",
        _base_context(
            request,
            clients=clients,
            search_by=search_by or "nom",
            search_value=search_value or "",
            sort_by=sort_by or "nom",
            sort_dir=sort_dir,
        ),
    )


@require_http_methods(["GET", "POST"])
def client_create(request):
    form = ClientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            get_service().clients.create(form.cleaned_data)
            messages.success(request, "Client ajouté avec succès.")
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Création impossible : {exc}")
        return redirect("travel:client_list")
    return render(request, "travel/client_form.html", _base_context(request, form=form, mode="create"))


@require_http_methods(["GET", "POST"])
def client_update(request, pk):
    service = get_service()
    item = service.clients.get(pk)
    if not item:
        messages.error(request, "Client introuvable.")
        return redirect("travel:client_list")
    initial = {
        "nom": item.get("nom", ""),
        "prenom": item.get("prenom", ""),
        "telephone": item.get("telephone", "") or "",
        "email": item.get("email", "") or "",
        "adresse": item.get("adresse", "") or "",
    }
    form = ClientForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            service.clients.update(pk, form.cleaned_data)
            messages.success(request, "Client modifié avec succès.")
            return redirect("travel:client_list")
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Modification impossible : {exc}")
    return render(
        request,
        "travel/client_form.html",
        _base_context(request, form=form, mode="update", item=item),
    )


@require_http_methods(["POST"])
def client_delete(request, pk):
    try:
        get_service().clients.delete(pk)
        messages.success(request, "Client supprimé.")
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Suppression impossible : {exc}")
    return redirect("travel:client_list")


# --------------------------------------------------------------------- #
# Destinations
# --------------------------------------------------------------------- #
def destination_list(request):
    service = get_service()
    search_by = request.GET.get("search_by")
    search_value = request.GET.get("search_value")
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir", "ASC")
    try:
        destinations = service.destinations.list(**_split_search(search_by, search_value, sort_by, sort_dir, "pays"))
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Erreur Oracle : {exc}")
        destinations = []
    return render(
        request,
        "travel/destination_list.html",
        _base_context(
            request,
            destinations=destinations,
            search_by=search_by or "pays",
            search_value=search_value or "",
            sort_by=sort_by or "pays",
            sort_dir=sort_dir,
        ),
    )


@require_http_methods(["GET", "POST"])
def destination_create(request):
    form = DestinationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            get_service().destinations.create(form.cleaned_data)
            messages.success(request, "Destination ajoutée avec succès.")
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Création impossible : {exc}")
        return redirect("travel:destination_list")
    return render(request, "travel/destination_form.html", _destination_form_context(request, form=form, mode="create"))


@require_http_methods(["GET", "POST"])
def destination_update(request, pk):
    service = get_service()
    item = service.destinations.get(pk)
    if not item:
        messages.error(request, "Destination introuvable.")
        return redirect("travel:destination_list")
    initial = {
        "pays": item.get("pays", ""),
        "ville": item.get("ville", ""),
        "description": item.get("description", "") or "",
        "prix_base": item.get("prix_base", ""),
        "image_path": item.get("image_path", "") or "",
    }
    form = DestinationForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            service.destinations.update(pk, form.cleaned_data)
            messages.success(request, "Destination modifiée avec succès.")
            return redirect("travel:destination_list")
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Modification impossible : {exc}")
    return render(
        request,
        "travel/destination_form.html",
        _destination_form_context(request, form=form, mode="update", item=item),
    )


@require_http_methods(["POST"])
def destination_delete(request, pk):
    try:
        get_service().destinations.delete(pk)
        messages.success(request, "Destination supprimée.")
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Suppression impossible : {exc}")
    return redirect("travel:destination_list")


# --------------------------------------------------------------------- #
# Voyages
# --------------------------------------------------------------------- #
def voyage_list(request):
    service = get_service()
    search_by = request.GET.get("search_by")
    search_value = request.GET.get("search_value")
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir", "ASC")
    try:
        voyages = service.voyages.list(**_split_search(search_by, search_value, sort_by, sort_dir, "date_depart"))
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Erreur Oracle : {exc}")
        voyages = []
    return render(
        request,
        "travel/voyage_list.html",
        _base_context(
            request,
            voyages=voyages,
            search_by=search_by or "destination",
            search_value=search_value or "",
            sort_by=sort_by or "date_depart",
            sort_dir=sort_dir,
        ),
    )


def _load_form_options():
    service = get_service()
    return {
        "destinations": service.destinations.list(),
    }


@require_http_methods(["GET", "POST"])
def voyage_create(request):
    options = _load_form_options()
    form = VoyageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            get_service().voyages.create(form.cleaned_data)
            messages.success(request, "Voyage créé avec succès.")
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Création impossible : {exc}")
        return redirect("travel:voyage_list")
    return render(
        request,
        "travel/voyage_form.html",
        _base_context(request, form=form, mode="create", destinations=options["destinations"]),
    )


@require_http_methods(["GET", "POST"])
def voyage_update(request, pk):
    service = get_service()
    options = _load_form_options()
    item = service.voyages.list(search_by=None, search_value=None)  # to leverage joined fields
    target = next((row for row in item if int(row.get("id_voyage", 0)) == int(pk)), None)
    if not target:
        messages.error(request, "Voyage introuvable.")
        return redirect("travel:voyage_list")
    initial = {
        "id_destination": target.get("id_destination"),
        "date_depart": format_date(target.get("date_depart")),
        "date_retour": format_date(target.get("date_retour")),
        "prix": target.get("prix"),
        "places_disponibles": target.get("places_disponibles"),
    }
    form = VoyageForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            service.voyages.update(pk, form.cleaned_data)
            messages.success(request, "Voyage modifié avec succès.")
            return redirect("travel:voyage_list")
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Modification impossible : {exc}")
    return render(
        request,
        "travel/voyage_form.html",
        _base_context(
            request,
            form=form,
            mode="update",
            item=target,
            destinations=options["destinations"],
        ),
    )


@require_http_methods(["POST"])
def voyage_delete(request, pk):
    try:
        get_service().voyages.delete(pk)
        messages.success(request, "Voyage supprimé.")
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Suppression impossible : {exc}")
    return redirect("travel:voyage_list")


# --------------------------------------------------------------------- #
# Reservations
# --------------------------------------------------------------------- #
def reservation_list(request):
    service = get_service()
    search_by = request.GET.get("search_by")
    search_value = request.GET.get("search_value")
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir", "ASC")
    try:
        reservations = service.reservations.list(
            **_split_search(search_by, search_value, sort_by, sort_dir, "date_reservation")
        )
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Erreur Oracle : {exc}")
        reservations = []
    return render(
        request,
        "travel/reservation_list.html",
        _base_context(
            request,
            reservations=reservations,
            search_by=search_by or "client",
            search_value=search_value or "",
            sort_by=sort_by or "date_reservation",
            sort_dir=sort_dir,
        ),
    )


def _load_reservation_options():
    service = get_service()
    clients = service.clients.list()
    voyages = service.voyages.list()
    return {"clients": clients, "voyages": voyages}


@require_http_methods(["GET", "POST"])
def reservation_create(request):
    options = _load_reservation_options()
    initial = {
        "date_reservation": date.today().strftime("%Y-%m-%d"),
        "status": "EN ATTENTE",
    }
    form = ReservationForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            get_service().create_reservation(form.cleaned_data)
            messages.success(request, "Réservation créée avec succès.")
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Création impossible : {exc}")
        return redirect("travel:reservation_list")
    return render(
        request,
        "travel/reservation_form.html",
        _base_context(
            request,
            form=form,
            mode="create",
            clients=options["clients"],
            voyages=options["voyages"],
        ),
    )


@require_http_methods(["GET", "POST"])
def reservation_update(request, pk):
    service = get_service()
    options = _load_reservation_options()
    reservations = service.reservations.list()
    target = next((row for row in reservations if int(row.get("id_reservation", 0)) == int(pk)), None)
    if not target:
        messages.error(request, "Réservation introuvable.")
        return redirect("travel:reservation_list")
    initial = {
        "id_client": target.get("id_client"),
        "id_voyage": target.get("id_voyage"),
        "date_reservation": format_date(target.get("date_reservation")),
        "nombre_personnes": target.get("nombre_personnes"),
        "status": target.get("status", "EN ATTENTE"),
    }
    form = ReservationForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            service.update_reservation(pk, form.cleaned_data)
            messages.success(request, "Réservation modifiée avec succès.")
            return redirect("travel:reservation_list")
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Modification impossible : {exc}")
    return render(
        request,
        "travel/reservation_form.html",
        _base_context(
            request,
            form=form,
            mode="update",
            item=target,
            clients=options["clients"],
            voyages=options["voyages"],
        ),
    )


@require_http_methods(["POST"])
def reservation_delete(request, pk):
    try:
        get_service().delete_reservation(pk)
        messages.success(request, "Réservation supprimée.")
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Suppression impossible : {exc}")
    return redirect("travel:reservation_list")


# --------------------------------------------------------------------- #
# Filters
# --------------------------------------------------------------------- #
def filters(request):
    mode = request.GET.get("mode", "voyages")
    sql_text = ""
    rows = []
    voyage_form = FilterVoyageForm(request.GET or None)
    reservation_form = FilterReservationForm(request.GET or None)

    if request.GET.get("apply"):
        service = get_service()
        try:
            if mode == "voyages":
                if voyage_form.is_valid():
                    sql, rows = service.filter_voyages(
                        {
                            k: (v.isoformat() if hasattr(v, "isoformat") else v)
                            for k, v in voyage_form.cleaned_data.items()
                            if v not in (None, "")
                        }
                    )
                else:
                    sql, rows = service.filter_voyages({})
            else:
                if reservation_form.is_valid():
                    sql, rows = service.filter_reservations(
                        {
                            k: (v.isoformat() if hasattr(v, "isoformat") else v)
                            for k, v in reservation_form.cleaned_data.items()
                            if v not in (None, "")
                        }
                    )
                else:
                    sql, rows = service.filter_reservations({})
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Filtrage impossible : {exc}")
        if sql:
            sql_text = " ".join(sql.split())

    return render(
        request,
        "travel/filters.html",
        _base_context(
            request,
            mode=mode,
            voyage_form=voyage_form,
            reservation_form=reservation_form,
            rows=rows,
            sql_text=sql_text,
        ),
    )


# --------------------------------------------------------------------- #
# SQL examples
# --------------------------------------------------------------------- #
def sql_examples(request):
    service = get_service()
    examples = QUERY_EXAMPLES
    selected_key = request.GET.get("example")
    keys = [key for key, _ in examples]
    if selected_key not in keys:
        selected_key = keys[0] if keys else None
    selected_sql = ""
    rows = []
    error = None
    if selected_key is not None:
        selected_sql = dict(examples)[selected_key].strip()
        try:
            rows = service.database.fetch_all(selected_sql)
        except Exception as exc:  # noqa: BLE001
            error = str(exc)

    return render(
        request,
        "travel/sql_examples.html",
        _base_context(
            request,
            keys=keys,
            selected_key=selected_key,
            selected_sql=selected_sql,
            rows=rows,
            error=error,
        ),
    )


# --------------------------------------------------------------------- #
# CSV export
# --------------------------------------------------------------------- #
class _Echo:
    """File-like object that just returns whatever is written to it."""

    def write(self, value):
        return value


def _reservations_to_csv():
    """Stream all reservations as CSV (UTF-8 with BOM for Excel)."""
    service = get_service()
    rows = service.reservations.list()
    pseudo = _Echo()
    writer = csv.writer(pseudo, delimiter=";")
    yield "\ufeff"  # BOM so Excel detects UTF-8
    yield writer.writerow([
        "ID", "Client", "Voyage", "Pays", "Ville",
        "Date réservation", "Personnes", "Statut", "Montant (€)",
    ])
    for row in rows:
        yield writer.writerow([
            row.get("id_reservation", ""),
            f'{row.get("prenom", "")} {row.get("nom", "")}'.strip(),
            f'#{row.get("id_voyage", "")}',
            row.get("pays", ""),
            row.get("ville", ""),
            (str(row.get("date_reservation", "")) or "")[:10],
            row.get("nombre_personnes", ""),
            row.get("status", ""),
            row.get("montant", ""),
        ])


@require_http_methods(["GET"])
def export_reservations_csv(request):
    """Return a CSV file with every reservation."""
    response = StreamingHttpResponse(_reservations_to_csv(), content_type="text/csv; charset=utf-8")
    filename = f"reservations_{date.today().isoformat()}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# --------------------------------------------------------------------- #
# Image upload (used by the destination form)
# --------------------------------------------------------------------- #
_ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}
_MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8 MB


@csrf_protect
@require_http_methods(["POST"])
def upload_image(request):
    """Accept an image POST and return its public URL.

    The destination form POSTs the picked file here, then stores the
    returned URL into the ``image_path`` hidden field before submit.
    """
    uploaded = request.FILES.get("file")
    if not uploaded:
        return JsonResponse({"ok": False, "error": "Aucun fichier reçu."}, status=400)

    ext = Path(uploaded.name).suffix.lower()
    if ext not in _ALLOWED_IMAGE_EXTS:
        return JsonResponse(
            {"ok": False, "error": f"Format non supporté ({ext or 'inconnu'}). Utilisez jpg, png, gif, webp ou avif."},
            status=400,
        )
    if uploaded.size > _MAX_IMAGE_BYTES:
        return JsonResponse(
            {"ok": False, "error": f"Image trop volumineuse ({uploaded.size // (1024 * 1024)} Mo). Maximum 8 Mo."},
            status=400,
        )

    safe_name = f"{uuid.uuid4().hex}{ext}"
    save_path = f"destinations/{safe_name}"
    saved_name = default_storage.save(save_path, uploaded)
    public_url = settings.MEDIA_URL.rstrip("/") + "/" + saved_name
    return JsonResponse({"ok": True, "url": public_url, "name": safe_name})
