from django import forms
from django.db import models
from wagtail.models import Orderable, ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey, ParentalManyToManyField

from apps.community.constants import VOICE_PART_CHOICES


class Role(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom", help_text="Nom de la fonction")
    description = models.TextField(null=True, blank=True, verbose_name="Description")

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
    ]

    class Meta:
        verbose_name = "Fonction"
        verbose_name_plural = "Fonctions"
        ordering = ['name']

    def __str__(self):
        return self.name


class Choriste(ClusterableModel):
    active = models.BooleanField(default=False, verbose_name="Actif")
    name = models.CharField(max_length=255, verbose_name="Nom", help_text="Nom du choriste")
    pupitre = models.CharField(choices=VOICE_PART_CHOICES, max_length=25, null=True, blank=True, verbose_name="Pupitre")
    mail = models.EmailField(null=True, blank=True, verbose_name="Email")
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="Téléphone")
    birthdate = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    choir_functions = ParentalManyToManyField(
        'Role',
        blank=True,
        related_name='choristes',
        verbose_name="Fonctions",
        help_text="Fonctions dans le chœur"
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('active'),
        FieldPanel('pupitre'),
        FieldPanel('mail'),
        FieldPanel('phone'),
        FieldPanel('birthdate'),
        InlinePanel('addresses', label="Adresse", max_num=1),
        FieldPanel('choir_functions', widget=forms.CheckboxSelectMultiple),
    ]

    class Meta:
        verbose_name = "Choriste"
        verbose_name_plural = "Choristes"

    def __str__(self):
        return self.name


class Address(Orderable):
    choriste = ParentalKey(
        'Choriste',
        on_delete=models.CASCADE,
        related_name='addresses',
        null=True,
        verbose_name="Choriste"
    )
    street = models.CharField(max_length=255, verbose_name="Rue")
    zip_code = models.CharField(max_length=10, verbose_name="Code postal")
    city = models.CharField(max_length=255, verbose_name="Localité")

    panels = [
        FieldPanel('street'),
        FieldPanel('zip_code'),
        FieldPanel('city'),
    ]

    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresses"

    def __str__(self):
        return f"{self.street}, {self.zip_code} {self.city}"
