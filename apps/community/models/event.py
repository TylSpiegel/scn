from datetime import datetime, time

from django.db import models
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from modelcluster.models import ClusterableModel
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase


class EventTag(TaggedItemBase):
    content_object = ParentalKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='tagged_items'
    )


class Event(ClusterableModel):
    name = models.CharField(max_length=255, verbose_name="Nom de l'événement")
    short_description = models.CharField(
        max_length=255, blank=True,
        verbose_name="Description courte",
        help_text="Résumé affiché dans la liste (facultatif)"
    )
    long_description = RichTextField(
        blank=True,
        verbose_name="Description longue",
        help_text="Détails affichés dans la fenêtre d'expansion (facultatif)"
    )
    tags = ClusterTaggableManager(through=EventTag, blank=True, verbose_name="Tags")

    start_date = models.DateField(
        verbose_name="Date de début",
        help_text="Date de début de l'événement (obligatoire)"
    )
    end_date = models.DateField(
        null=True, blank=True,
        verbose_name="Date de fin",
        help_text="Date de fin (si différente de la date de début)"
    )

    time_tbd = models.BooleanField(
        default=False,
        verbose_name="Heure à déterminer",
        help_text="Cochez si l'heure n'est pas encore fixée"
    )
    start_time = models.TimeField(null=True, blank=True, verbose_name="Heure de début")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Heure de fin")

    lieu = models.CharField(null=True, blank=True, max_length=250, verbose_name="Lieu")
    adresse = models.CharField(null=True, blank=True, max_length=250, verbose_name="Adresse")

    panels = [
        FieldPanel('name'),
        FieldPanel('tags'),
        FieldPanel('short_description'),
        FieldPanel('long_description'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('start_date', classname="col6"),
                FieldPanel('end_date', classname="col6"),
            ]),
            FieldPanel('time_tbd'),
            FieldRowPanel([
                FieldPanel('start_time', classname="col6"),
                FieldPanel('end_time', classname="col6"),
            ]),
        ], heading="Dates et heures"),
        MultiFieldPanel([
            FieldPanel('lieu'),
            FieldPanel('adresse'),
        ], heading="Localisation"),
    ]

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['start_date', 'start_time']

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.end_date:
            self.end_date = self.start_date
        if self.end_date < self.start_date:
            raise ValidationError({'end_date': 'La date de fin ne peut pas être antérieure à la date de début.'})
        if self.time_tbd and (self.start_time or self.end_time):
            raise ValidationError({'time_tbd': 'Si "Heure à déterminer" est coché, les heures doivent être vides.'})
        if self.end_time and not self.start_time:
            raise ValidationError({'end_time': 'Vous devez définir une heure de début si vous définissez une heure de fin.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        date_str = self.start_date.strftime('%d-%m')
        if self.time_tbd:
            time_str = " (heure TBD)"
        elif self.start_time:
            time_str = f" {self.start_time.strftime('%H:%M')}"
        else:
            time_str = ""
        return f"{date_str}{time_str} // {self.name}"

    @property
    def display_time(self):
        if self.time_tbd:
            return "Heure à déterminer"
        elif self.start_time:
            if self.end_time:
                return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
            return self.start_time.strftime('%H:%M')
        return ""

    @property
    def datetime_start(self):
        if self.start_time:
            return datetime.combine(self.start_date, self.start_time)
        return datetime.combine(self.start_date, time(0, 0))

    @property
    def datetime_end(self):
        end_date = self.end_date if self.end_date else self.start_date
        if self.end_time:
            return datetime.combine(end_date, self.end_time)
        return None
