"""
EventType Model

A model to define different types of events (rehearsals, concerts, etc.) with their default settings.
Each event type can have:
- Basic info (name, description, color coding, icon)
- Default schedule (start/end times)
- Default location

Maybe in the future :
- Behavioral settings (attendance requirements, notifications)

Used to create event templates that streamline event creation and maintain consistency.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from wagtail_color_panel.fields import ColorField


@register_snippet
class EventType(models.Model):
   name = models.CharField("Nom", max_length=100)
   is_rehearsal = models.BooleanField("Est une répétition", default=False)
   description = models.TextField("Description", blank=True)
   color = ColorField("Couleur", default='#FF0000') 
   icon = models.CharField("Icône", max_length=50, blank=True, help_text="Nom de l'icône FontAwesome")
   
   # Default schedule
   default_start_time = models.TimeField("Heure de début par défaut", null=True, blank=True)
   default_end_time = models.TimeField("Heure de fin par défaut", null=True, blank=True)
   
   # Default location
   default_location = models.CharField("Lieu par défaut", max_length=250, blank=True)
   default_address = models.CharField("Adresse par défaut", max_length=250, blank=True)
   
   panels = [
       MultiFieldPanel([
           FieldPanel('name'),
           FieldPanel('description'),
           FieldPanel('is_rehearsal'),
           FieldPanel('color'),
           FieldPanel('icon'),
       ], heading="Informations générales"),
       MultiFieldPanel([
           FieldPanel('default_start_time'),
           FieldPanel('default_end_time'),
           FieldPanel('default_duration'),
       ], heading="Horaires par défaut"),
       MultiFieldPanel([
           FieldPanel('default_location'),
           FieldPanel('default_address'),
       ], heading="Lieu par défaut"),
   ]

   def __str__(self):
       return self.name

   class Meta:
       verbose_name = "Type d'événement"
       verbose_name_plural = "Types d'événement"