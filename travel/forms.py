"""
Django forms for the travel app.

These forms intentionally avoid using the Django ORM (which is not bound
to the Oracle database in this project). They validate raw dictionaries
coming from POST requests before the underlying
``app.services.travel_service.TravelService`` performs the actual
insert/update/delete through ``python-oracledb``.
"""
from decimal import Decimal, InvalidOperation

from django import forms


def _strip(value):
    return value.strip() if isinstance(value, str) else value


_TEXT = {"class": "form-input"}
_TEXTAREA = {"class": "form-textarea", "rows": 3}
_NUMBER = {"class": "form-input", "step": "any", "min": "0"}
_DATE = {"class": "form-input", "type": "date"}


class ClientForm(forms.Form):
    nom = forms.CharField(max_length=80, widget=forms.TextInput(attrs=_TEXT))
    prenom = forms.CharField(max_length=80, widget=forms.TextInput(attrs=_TEXT))
    telephone = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs=_TEXT))
    email = forms.EmailField(max_length=120, required=False, widget=forms.EmailInput(attrs=_TEXT))
    adresse = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs=_TEXTAREA))

    def clean(self):
        cleaned = super().clean()
        for key in cleaned:
            cleaned[key] = _strip(cleaned.get(key) or "")
        return cleaned


class DestinationForm(forms.Form):
    pays = forms.CharField(max_length=80, widget=forms.TextInput(attrs=_TEXT))
    ville = forms.CharField(max_length=80, widget=forms.TextInput(attrs=_TEXT))
    description = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs=_TEXTAREA))
    prix_base = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs=_NUMBER),
    )
    image_path = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs=_TEXT))

    def clean(self):
        cleaned = super().clean()
        for key in cleaned:
            cleaned[key] = _strip(cleaned.get(key) or "")
        return cleaned


class VoyageForm(forms.Form):
    id_destination = forms.IntegerField(widget=forms.Select(attrs={"class": "form-select"}))
    date_depart = forms.DateField(input_formats=["%Y-%m-%d"], widget=forms.DateInput(attrs=_DATE))
    date_retour = forms.DateField(input_formats=["%Y-%m-%d"], widget=forms.DateInput(attrs=_DATE))
    prix = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs=_NUMBER),
    )
    places_disponibles = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={"class": "form-input", "min": "0"}))

    def clean(self):
        cleaned = super().clean()
        date_depart = cleaned.get("date_depart")
        date_retour = cleaned.get("date_retour")
        if date_depart and date_retour and date_retour < date_depart:
            raise forms.ValidationError("La date de retour doit être postérieure à la date de départ.")
        return cleaned


class ReservationForm(forms.Form):
    id_client = forms.IntegerField(widget=forms.Select(attrs={"class": "form-select"}))
    id_voyage = forms.IntegerField(widget=forms.Select(attrs={"class": "form-select"}))
    date_reservation = forms.DateField(
        input_formats=["%Y-%m-%d"],
        required=False,
        widget=forms.DateInput(attrs=_DATE),
    )
    nombre_personnes = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={"class": "form-input", "min": "1"}))
    status = forms.ChoiceField(
        choices=[
            ("EN ATTENTE", "En attente"),
            ("CONFIRMÉ", "Confirmé"),
            ("ANNULÉ", "Annulé"),
        ],
        initial="EN ATTENTE",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class FilterVoyageForm(forms.Form):
    pays = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    ville = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    date_depart = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"class": "form-input", "type": "date"}),
    )
    date_retour = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"class": "form-input", "type": "date"}),
    )
    prix_min = forms.DecimalField(
        required=False,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "any", "min": "0"}),
    )
    prix_max = forms.DecimalField(
        required=False,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "any", "min": "0"}),
    )


class FilterReservationForm(forms.Form):
    client = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    voyage = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    date_reservation = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"class": "form-input", "type": "date"}),
    )
    montant_min = forms.DecimalField(
        required=False,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "any", "min": "0"}),
    )
    montant_max = forms.DecimalField(
        required=False,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "any", "min": "0"}),
    )


def parse_decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None
