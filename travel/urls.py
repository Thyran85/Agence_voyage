"""URL routing for the travel app."""
from django.urls import path

from travel import views

app_name = "travel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Clients
    path("clients/", views.client_list, name="client_list"),
    path("clients/nouveau/", views.client_create, name="client_create"),
    path("clients/<int:pk>/modifier/", views.client_update, name="client_update"),
    path("clients/<int:pk>/supprimer/", views.client_delete, name="client_delete"),
    # Destinations
    path("destinations/", views.destination_list, name="destination_list"),
    path("destinations/nouveau/", views.destination_create, name="destination_create"),
    path("destinations/<int:pk>/modifier/", views.destination_update, name="destination_update"),
    path("destinations/<int:pk>/supprimer/", views.destination_delete, name="destination_delete"),
    # Voyages
    path("voyages/", views.voyage_list, name="voyage_list"),
    path("voyages/nouveau/", views.voyage_create, name="voyage_create"),
    path("voyages/<int:pk>/modifier/", views.voyage_update, name="voyage_update"),
    path("voyages/<int:pk>/supprimer/", views.voyage_delete, name="voyage_delete"),
    # Reservations
    path("reservations/", views.reservation_list, name="reservation_list"),
    path("reservations/nouveau/", views.reservation_create, name="reservation_create"),
    path("reservations/<int:pk>/modifier/", views.reservation_update, name="reservation_update"),
    path("reservations/<int:pk>/supprimer/", views.reservation_delete, name="reservation_delete"),
    # Filters & SQL playground
    path("filtres/", views.filters, name="filters"),
    path("sql/", views.sql_examples, name="sql_examples"),
    # CSV export
    path("reservations/export/csv/", views.export_reservations_csv, name="export_reservations_csv"),
    # Image upload
    path("upload/image/", views.upload_image, name="upload_image"),
]
