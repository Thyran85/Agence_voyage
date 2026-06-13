"""Views for the travel app."""
import csv
import json
import logging
import uuid
from datetime import date
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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

logger = logging.getLogger(__name__)


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
    "madagascar": "/static/travel/img/destinations/antananarivo.jpg",
    "antananarivo": "/static/travel/img/destinations/antananarivo.jpg",
    "nosybe": "/static/travel/img/destinations/nosybe.jpg",
    "toliara": "/static/travel/img/destinations/toliara.jpg",
    "ilesaintemarie": "/static/travel/img/destinations/sainte-marie.jpg",
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
@login_required
def dashboard(request):
    service = get_service()
    try:
        stats = service.dashboard_stats()
        recent = service.recent_reservations(limit=4)
    except ConnectionError:
        logger.exception("Dashboard - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré et que le service TNS est accessible.")
        stats = {"clients": 0, "destinations": 0, "voyages": 0, "reservations": 0, "destination_top": None, "voyage_top": None}
        recent = []
    except RuntimeError as e:
        logger.exception("Dashboard - erreur métier")
        messages.error(request, str(e))
        stats = {"clients": 0, "destinations": 0, "voyages": 0, "reservations": 0, "destination_top": None, "voyage_top": None}
        recent = []
    except Exception:  # noqa: BLE001
        logger.exception("Dashboard - erreur inattendue")
        messages.error(request, "Erreur inattendue lors du chargement du tableau de bord. Rechargez la page ou contactez l'administrateur.")
        stats = {"clients": 0, "destinations": 0, "voyages": 0, "reservations": 0, "destination_top": None, "voyage_top": None}
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
@login_required
def client_list(request):
    service = get_service()
    search_by = request.GET.get("search_by")
    search_value = request.GET.get("search_value")
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir", "ASC")
    try:
        clients = service.clients.list(**_split_search(search_by, search_value, sort_by, sort_dir, "nom"))
    except ConnectionError:
        logger.exception("Client list - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        clients = []
    except RuntimeError as e:
        logger.exception("Client list - erreur métier")
        messages.error(request, str(e))
        clients = []
    except Exception:  # noqa: BLE001
        logger.exception("Client list - erreur inattendue")
        messages.error(request, "Erreur inattendue lors du chargement des clients. Rechargez la page.")
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


@login_required
@require_http_methods(["GET", "POST"])
def client_create(request):
    form = ClientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            get_service().clients.create(form.cleaned_data)
            messages.success(request, "Client ajouté avec succès.")
        except ConnectionError:
            logger.exception("Client creation - connexion perdue")
            messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        except ValueError as e:
            logger.exception("Client creation - validation")
            messages.error(request, str(e))
        except RuntimeError as e:
            logger.exception("Client creation - erreur métier")
            messages.error(request, str(e))
        except Exception:  # noqa: BLE001
            logger.exception("Client creation - erreur inattendue")
            messages.error(request, "Création impossible. Vérifiez les données saisies et réessayez.")
        return redirect("travel:client_list")
    return render(request, "travel/client_form.html", _base_context(request, form=form, mode="create"))


@login_required
@require_http_methods(["GET", "POST"])
def client_update(request, pk):
    try:
        service = get_service()
        item = service.clients.get(pk)
    except ConnectionError:
        logger.exception("Client fetch - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        return redirect("travel:client_list")
    except RuntimeError as e:
        logger.exception("Client fetch - erreur")
        messages.error(request, str(e))
        return redirect("travel:client_list")
    except Exception:  # noqa: BLE001
        logger.exception("Client fetch - erreur inattendue")
        messages.error(request, "Erreur inattendue. Rechargez la page ou contactez l'administrateur.")
        return redirect("travel:client_list")
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
        except ConnectionError:
            logger.exception("Client update - connexion perdue")
            messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        except ValueError as e:
            logger.exception("Client update - validation")
            messages.error(request, str(e))
        except RuntimeError as e:
            logger.exception("Client update - erreur")
            messages.error(request, str(e))
        except Exception:  # noqa: BLE001
            logger.exception("Client update - erreur inattendue")
            messages.error(request, "Modification impossible. Vérifiez les données et réessayez.")
    return render(
        request,
        "travel/client_form.html",
        _base_context(request, form=form, mode="update", item=item),
    )


@login_required
@require_http_methods(["POST"])
def client_delete(request, pk):
    try:
        nb_reservations = get_service().delete_client_with_reservations(pk)
        if nb_reservations:
            messages.success(request, f"Client supprimé avec {nb_reservations} réservation(s) liée(s).")
        else:
            messages.success(request, "Client supprimé.")
    except ConnectionError:
        logger.exception("Client delete - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
    except RuntimeError as e:
        logger.exception("Client delete - erreur")
        messages.error(request, str(e))
    except Exception:  # noqa: BLE001
        logger.exception("Client delete - erreur inattendue")
        messages.error(request, "Suppression impossible. Vérifiez que le client n'a pas de réservations liées.")
    return redirect("travel:client_list")


# --------------------------------------------------------------------- #
# Destinations
# --------------------------------------------------------------------- #
@login_required
def destination_list(request):
    service = get_service()
    search_by = request.GET.get("search_by")
    search_value = request.GET.get("search_value")
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir", "ASC")
    try:
        destinations = service.destinations.list(**_split_search(search_by, search_value, sort_by, sort_dir, "pays"))
    except ConnectionError:
        logger.exception("Destination list - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        destinations = []
    except RuntimeError as e:
        logger.exception("Destination list - erreur")
        messages.error(request, str(e))
        destinations = []
    except Exception:  # noqa: BLE001
        logger.exception("Destination list - erreur inattendue")
        messages.error(request, "Erreur inattendue lors du chargement des destinations. Rechargez la page.")
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


@login_required
@require_http_methods(["GET", "POST"])
def destination_create(request):
    form = DestinationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            get_service().destinations.create(form.cleaned_data)
            messages.success(request, "Destination ajoutée avec succès.")
        except ConnectionError:
            logger.exception("Destination creation - connexion perdue")
            messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        except ValueError as e:
            logger.exception("Destination creation - validation")
            messages.error(request, str(e))
        except RuntimeError as e:
            logger.exception("Destination creation - erreur")
            messages.error(request, str(e))
        except Exception:  # noqa: BLE001
            logger.exception("Destination creation - erreur inattendue")
            messages.error(request, "Création impossible. Vérifiez les données saisies et réessayez.")
        return redirect("travel:destination_list")
    return render(request, "travel/destination_form.html", _destination_form_context(request, form=form, mode="create"))


@login_required
@require_http_methods(["GET", "POST"])
def destination_update(request, pk):
    try:
        service = get_service()
        item = service.destinations.get(pk)
    except ConnectionError:
        logger.exception("Destination fetch - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        return redirect("travel:destination_list")
    except RuntimeError as e:
        logger.exception("Destination fetch - erreur")
        messages.error(request, str(e))
        return redirect("travel:destination_list")
    except Exception:  # noqa: BLE001
        logger.exception("Destination fetch - erreur inattendue")
        messages.error(request, "Erreur inattendue. Rechargez la page ou contactez l'administrateur.")
        return redirect("travel:destination_list")
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
        except ConnectionError:
            logger.exception("Destination update - connexion perdue")
            messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        except ValueError as e:
            logger.exception("Destination update - validation")
            messages.error(request, str(e))
        except RuntimeError as e:
            logger.exception("Destination update - erreur")
            messages.error(request, str(e))
        except Exception:  # noqa: BLE001
            logger.exception("Destination update - erreur inattendue")
            messages.error(request, "Modification impossible. Vérifiez les données et réessayez.")
    return render(
        request,
        "travel/destination_form.html",
        _destination_form_context(request, form=form, mode="update", item=item),
    )


@login_required
@require_http_methods(["POST"])
def destination_delete(request, pk):
    try:
        get_service().destinations.delete(pk)
        messages.success(request, "Destination supprimée.")
    except ConnectionError:
        logger.exception("Destination delete - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
    except RuntimeError as e:
        logger.exception("Destination delete - erreur")
        messages.error(request, str(e))
    except Exception:  # noqa: BLE001
        logger.exception("Destination delete - erreur inattendue")
        messages.error(request, "Suppression impossible. Vérifiez qu'aucun voyage n'est lié à cette destination.")
    return redirect("travel:destination_list")


# --------------------------------------------------------------------- #
# Voyages
# --------------------------------------------------------------------- #
@login_required
def voyage_list(request):
    service = get_service()
    search_by = request.GET.get("search_by")
    search_value = request.GET.get("search_value")
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir", "ASC")
    try:
        voyages = service.voyages.list(**_split_search(search_by, search_value, sort_by, sort_dir, "date_depart"))
    except ConnectionError:
        logger.exception("Voyage list - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        voyages = []
    except RuntimeError as e:
        logger.exception("Voyage list - erreur")
        messages.error(request, str(e))
        voyages = []
    except Exception:  # noqa: BLE001
        logger.exception("Voyage list - erreur inattendue")
        messages.error(request, "Erreur inattendue lors du chargement des voyages. Rechargez la page.")
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
    try:
        service = get_service()
        return {
            "destinations": service.destinations.list(),
        }
    except ConnectionError:
        logger.exception("Form options - connexion perdue")
        return {"destinations": []}
    except Exception:  # noqa: BLE001
        logger.exception("Form options - erreur")
        return {"destinations": []}


@login_required
@require_http_methods(["GET", "POST"])
def voyage_create(request):
    options = _load_form_options()
    form = VoyageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            get_service().voyages.create(form.cleaned_data)
            messages.success(request, "Voyage créé avec succès.")
        except ConnectionError:
            logger.exception("Voyage creation - connexion perdue")
            messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        except ValueError as e:
            logger.exception("Voyage creation - validation")
            messages.error(request, str(e))
        except RuntimeError as e:
            logger.exception("Voyage creation - erreur")
            messages.error(request, str(e))
        except Exception:  # noqa: BLE001
            logger.exception("Voyage creation - erreur inattendue")
            messages.error(request, "Création impossible. Vérifiez les données saisies et réessayez.")
        return redirect("travel:voyage_list")
    return render(
        request,
        "travel/voyage_form.html",
        _base_context(request, form=form, mode="create", destinations=options["destinations"]),
    )


@login_required
@require_http_methods(["GET", "POST"])
def voyage_update(request, pk):
    try:
        service = get_service()
        options = _load_form_options()
        item = service.voyages.list(search_by=None, search_value=None)
    except ConnectionError:
        logger.exception("Voyage fetch - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        return redirect("travel:voyage_list")
    except RuntimeError as e:
        logger.exception("Voyage fetch - erreur")
        messages.error(request, str(e))
        return redirect("travel:voyage_list")
    except Exception:  # noqa: BLE001
        logger.exception("Voyage fetch - erreur inattendue")
        messages.error(request, "Erreur inattendue. Rechargez la page ou contactez l'administrateur.")
        return redirect("travel:voyage_list")
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
        except ConnectionError:
            logger.exception("Voyage update - connexion perdue")
            messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        except ValueError as e:
            logger.exception("Voyage update - validation")
            messages.error(request, str(e))
        except RuntimeError as e:
            logger.exception("Voyage update - erreur")
            messages.error(request, str(e))
        except Exception:  # noqa: BLE001
            logger.exception("Voyage update - erreur inattendue")
            messages.error(request, "Modification impossible. Vérifiez les données et réessayez.")
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


@login_required
@require_http_methods(["POST"])
def voyage_delete(request, pk):
    try:
        get_service().voyages.delete(pk)
        messages.success(request, "Voyage supprimé.")
    except ConnectionError:
        logger.exception("Voyage delete - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
    except RuntimeError as e:
        logger.exception("Voyage delete - erreur")
        messages.error(request, str(e))
    except Exception:  # noqa: BLE001
        logger.exception("Voyage delete - erreur inattendue")
        messages.error(request, "Suppression impossible. Vérifiez qu'aucune réservation n'est liée à ce voyage.")
    return redirect("travel:voyage_list")


# --------------------------------------------------------------------- #
# Reservations
# --------------------------------------------------------------------- #
@login_required
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
    except ConnectionError:
        logger.exception("Reservation list - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        reservations = []
    except RuntimeError as e:
        logger.exception("Reservation list - erreur")
        messages.error(request, str(e))
        reservations = []
    except Exception:  # noqa: BLE001
        logger.exception("Reservation list - erreur inattendue")
        messages.error(request, "Erreur inattendue lors du chargement des réservations. Rechargez la page.")
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
    try:
        service = get_service()
        clients = service.clients.list()
        voyages = service.voyages.list()
        return {"clients": clients, "voyages": voyages}
    except ConnectionError:
        logger.exception("Reservation options - connexion perdue")
        return {"clients": [], "voyages": []}
    except Exception:  # noqa: BLE001
        logger.exception("Reservation options - erreur")
        return {"clients": [], "voyages": []}


@login_required
@require_http_methods(["GET", "POST"])
def reservation_create(request):
    options = _load_reservation_options()
    initial = {
        "date_reservation": date.today().strftime("%Y-%m-%d"),
        "status": "CONFIRMÉ",
    }
    form = ReservationForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            get_service().create_reservation(form.cleaned_data)
            messages.success(request, "Réservation créée avec succès.")
        except ConnectionError:
            logger.exception("Reservation create - connexion perdue")
            messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        except ValueError as e:
            logger.exception("Reservation create - validation")
            messages.error(request, str(e))
        except RuntimeError as e:
            logger.exception("Reservation create - erreur")
            messages.error(request, str(e))
        except Exception:  # noqa: BLE001
            logger.exception("Reservation create - erreur inattendue")
            messages.error(request, "Création impossible. Vérifiez les données saisies et réessayez.")
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


@login_required
@require_http_methods(["GET", "POST"])
def reservation_update(request, pk):
    try:
        service = get_service()
        options = _load_reservation_options()
        reservations = service.reservations.list()
    except ConnectionError:
        logger.exception("Reservation fetch - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        return redirect("travel:reservation_list")
    except RuntimeError as e:
        logger.exception("Reservation fetch - erreur")
        messages.error(request, str(e))
        return redirect("travel:reservation_list")
    except Exception:  # noqa: BLE001
        logger.exception("Reservation fetch - erreur inattendue")
        messages.error(request, "Erreur inattendue. Rechargez la page ou contactez l'administrateur.")
        return redirect("travel:reservation_list")
    target = next((row for row in reservations if int(row.get("id_reservation", 0)) == int(pk)), None)
    if not target:
        messages.error(request, "Réservation introuvable.")
        return redirect("travel:reservation_list")
    initial = {
        "id_client": target.get("id_client"),
        "id_voyage": target.get("id_voyage"),
        "date_reservation": format_date(target.get("date_reservation")),
        "nombre_personnes": target.get("nombre_personnes"),
        "status": target.get("status", "CONFIRMÉ"),
    }
    form = ReservationForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            service.update_reservation(pk, form.cleaned_data)
            messages.success(request, "Réservation modifiée avec succès.")
            return redirect("travel:reservation_list")
        except ConnectionError:
            logger.exception("Reservation update - connexion perdue")
            messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        except ValueError as e:
            logger.exception("Reservation update - validation")
            messages.error(request, str(e))
        except RuntimeError as e:
            logger.exception("Reservation update - erreur")
            messages.error(request, str(e))
        except Exception:  # noqa: BLE001
            logger.exception("Reservation update - erreur inattendue")
            messages.error(request, "Modification impossible. Vérifiez les données et réessayez.")
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


@login_required
@require_http_methods(["POST"])
def reservation_delete(request, pk):
    try:
        get_service().delete_reservation(pk)
        messages.success(request, "Réservation supprimée.")
    except ConnectionError:
        logger.exception("Reservation delete - connexion perdue")
        messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
    except ValueError as e:
        logger.exception("Reservation delete - validation")
        messages.error(request, str(e))
    except RuntimeError as e:
        logger.exception("Reservation delete - erreur")
        messages.error(request, str(e))
    except Exception:  # noqa: BLE001
        logger.exception("Reservation delete - erreur inattendue")
        messages.error(request, "Suppression impossible. Rechargez la page et réessayez.")
    return redirect("travel:reservation_list")


# --------------------------------------------------------------------- #
# Filters
# --------------------------------------------------------------------- #
@login_required
def filters(request):
    mode = request.GET.get("mode", "voyages")
    sql_text = ""
    rows = []
    voyage_form = FilterVoyageForm(request.GET or None)
    reservation_form = FilterReservationForm(request.GET or None)

    if request.GET.get("apply"):
        service = get_service()
        sql = ""
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
        except ConnectionError:
            logger.exception("Filter - connexion perdue")
            messages.error(request, "Connexion à la base perdue. Vérifiez qu'Oracle est démarré.")
        except RuntimeError as e:
            logger.exception("Filter - erreur")
            messages.error(request, str(e))
        except Exception:  # noqa: BLE001
            logger.exception("Filter - erreur inattendue")
            messages.error(request, "Filtrage impossible. Vérifiez les critères saisis et réessayez.")
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
@login_required
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
        except ConnectionError:
            logger.exception("SQL example - connexion perdue")
            error = "Connexion à la base perdue. Vérifiez qu'Oracle est démarré."
        except RuntimeError as e:
            logger.exception("SQL example - erreur")
            error = str(e)
        except Exception:  # noqa: BLE001
            logger.exception("SQL example - erreur inattendue")
            error = "Erreur lors de l'exécution de la requête. Vérifiez la syntaxe SQL et réessayez."

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
    try:
        service = get_service()
        rows = service.reservations.list()
    except Exception:
        logger.exception("CSV export query failed")
        return
    pseudo = _Echo()
    writer = csv.writer(pseudo, delimiter=";")
    yield "\ufeff"  # BOM so Excel detects UTF-8
    yield writer.writerow([
        "ID", "Client", "Voyage", "Pays", "Ville",
        "Date réservation", "Personnes", "Statut", "Montant (Ar)",
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


@login_required
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


@login_required
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
    try:
        saved_name = default_storage.save(save_path, uploaded)
    except OSError:
        logger.exception("Image upload - fichier")
        return JsonResponse({"ok": False, "error": "Erreur d'écriture sur le disque. Vérifiez l'espace disponible et les permissions du dossier media/destinations/."}, status=500)
    except Exception:  # noqa: BLE001
        logger.exception("Image upload - erreur inattendue")
        return JsonResponse({"ok": False, "error": "Erreur lors de l'enregistrement du fichier. Réessayez ou contactez l'administrateur."}, status=500)
    public_url = settings.MEDIA_URL.rstrip("/") + "/" + saved_name
    return JsonResponse({"ok": True, "url": public_url, "name": safe_name})
