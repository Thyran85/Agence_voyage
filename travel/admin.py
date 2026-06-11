"""Django admin registration (Oracle tables only)."""
from django.contrib import admin

from travel.models import Client, Destination, Reservation, Voyage


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id_client", "nom", "prenom", "telephone", "email")
    search_fields = ("nom", "prenom", "email", "telephone")


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("id_destination", "pays", "ville", "prix_base")
    search_fields = ("pays", "ville")


@admin.register(Voyage)
class VoyageAdmin(admin.ModelAdmin):
    list_display = ("id_voyage", "id_destination", "date_depart", "date_retour", "prix", "places_disponibles")
    list_filter = ("id_destination",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id_reservation", "id_client", "id_voyage", "date_reservation", "nombre_personnes", "montant", "status")
    list_filter = ("status",)
