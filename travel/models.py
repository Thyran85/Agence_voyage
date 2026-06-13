"""
Django models for the travel app.

The application data lives in an Oracle database that is managed outside
of Django (see ``sql/schema.sql``). The models below are defined with
``managed = False`` so Django will not try to create, alter or drop any
of these tables. They are used purely to expose the schema to the
Django admin, the ORM query interface and form generation helpers.
"""
from django.db import models


class Client(models.Model):
    id_client = models.IntegerField(primary_key=True)
    nom = models.CharField(max_length=80)
    prenom = models.CharField(max_length=80)
    telephone = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=120, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "clients"
        ordering = ["nom", "prenom"]

    def __str__(self):
        return f"{self.nom} {self.prenom}".strip()


class Destination(models.Model):
    id_destination = models.IntegerField(primary_key=True)
    pays = models.CharField(max_length=80)
    ville = models.CharField(max_length=80)
    description = models.CharField(max_length=500, blank=True, null=True)
    prix_base = models.DecimalField(max_digits=10, decimal_places=2)
    image_path = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "destinations"
        ordering = ["pays", "ville"]

    def __str__(self):
        return f"{self.pays} - {self.ville}"


class Voyage(models.Model):
    id_voyage = models.IntegerField(primary_key=True)
    id_destination = models.IntegerField()
    date_depart = models.DateField()
    date_retour = models.DateField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    places_disponibles = models.IntegerField()

    class Meta:
        managed = False
        db_table = "voyages"
        ordering = ["date_depart"]


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("CONFIRMÉ", "Confirmé"),
        ("ANNULÉ", "Annulé"),
    ]

    id_reservation = models.IntegerField(primary_key=True)
    id_client = models.IntegerField()
    id_voyage = models.IntegerField()
    date_reservation = models.DateField()
    nombre_personnes = models.IntegerField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="CONFIRMÉ")

    class Meta:
        managed = False
        db_table = "reservations"
        ordering = ["-date_reservation"]
