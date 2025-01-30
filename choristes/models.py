import json
import sys

from datetime import timedelta, datetime

from django.db import models
from django.utils import timezone
from django.db.models.functions import ExtractMonth, ExtractYear
from django.core.validators import MaxValueValidator, MinValueValidator

from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import TabbedInterface, ObjectList
from wagtail.admin.panels import (
    FieldPanel,
)
from wagtail.documents.models import Document
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from .blocks import AudioDocumentBlock, AdditionalFilesBlock

PUPITRES_CHOICES = (
    ('Tutti', 'Tutti'),
    ('Soprano', 'Soprano'),
    ('Alto', 'Alto'),
    ('Ténor', 'Ténor'),
    ('Basse', 'Basse'),
    ('Autre', 'Autre'),
)

PUPITRES_COLORS = {
    'Tutti': '#007BFF',
    'Soprano': '#DC3545',
    'Alto': '#FFC107',
    'Ténor': '#28A745',
    'Basse': '#17A2B8',
    'Autre': '#6C757D',
}


## CURRENTLY NOT USED
class NewsPage(Page):
    titre = models.CharField(max_length=250, null=True)
    auteur = models.CharField(max_length=250, null=True)
    date = models.DateField("Post date")
    message = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('titre'),
        FieldPanel('auteur'),
        FieldPanel('date'),
        FieldPanel('message'),
    ]

    parent_page_types = []
    subpage_types = []


####                #####
#       MORCEAU         #
####                #####

class MorceauPage(Page):
    titre = models.CharField(max_length=250, null=True)
    compositeur = models.CharField(max_length=250, null=True, )
    descr = RichTextField(blank=True)
    traduction = RichTextField(blank=True)
    interpretation = RichTextField(blank=True)

    pdf = models.ForeignKey(
        Document,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    audios = StreamField([
        ('audios', AudioDocumentBlock()),
    ], null=True, blank=True, use_json_field=True)

    additional_files = StreamField([
        ('section', AdditionalFilesBlock()),
    ], null=True, blank=True, use_json_field=True)

    base_panels = Page.content_panels + [
        FieldPanel('titre'),
        FieldPanel('compositeur'),
        FieldPanel('descr'),
        FieldPanel('pdf'),
        FieldPanel('audios'),
        FieldPanel('additional_files')
    ]

    advanced_panels = [
        FieldPanel('traduction'),
    ]

    interpretation_panels = [
        FieldPanel('interpretation'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(base_panels, heading='Infos de base'),
        ObjectList(advanced_panels, heading='Texte, traduction et interprétation'),
        ObjectList(interpretation_panels, heading='Indications musicales'),
        ObjectList(Page.promote_panels, heading='Routing'),
    ])

    def get_context(self, request):
        context = super().get_context(request)
        context['audios'] = sorted(self.audios, key=lambda x: x.value['pupitre'])
        return context

    parent_page_types = ["MorceauIndexPage"]
    subpage_types = []


class MorceauIndexPage(Page):
    introduction = models.TextField(help_text="Text to describe the page", blank=True)
    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
    ]
    subpage_types = ["MorceauPage", "NewsPage"]

    def children(self):
        return self.get_children().specific().live()

    def get_context(self, request):
        context = super(MorceauIndexPage, self).get_context(request)
        context["morceau"] = (
            MorceauPage.objects.descendant_of(self).live()
        )
        return context


####                #####
#     CALENDRIER        #
####                #####

class CalendrierPage(Page):
    # OPTIONS

    # FIELDS
    how_many_events = models.IntegerField(blank=True, null=True, default=5, help_text="""
    Définir combien d'événements afficher dans la liste des prochains événements.""")

    show_calendar = models.BooleanField(default=True,
                                        help_text="""
    Est-ce que vous voulez que le widget calendrier s'affiche ? (max. 100)
    """,
                                        validators=[
                                            MinValueValidator(0),
                                            MaxValueValidator(100)
                                        ]
                                        )

    comment = RichTextField(
        blank=True,
        help_text="Un espace pour ajouter des commentaires : les changements récents, les prochaines dates..."
    )
    content_panels = Page.content_panels + [
        FieldPanel('comment'),
        FieldPanel('show_calendar'),
        FieldPanel('how_many_events'),
    ]

    def get_all_events(self):
        events = Evenement.objects.order_by('start_date').all()
        events_list = [
            {
                'title': f'{event.name} {event.pupitre}' if event.is_repetition else f'{event.name}',
                'start': event.start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                'end': event.end_date.strftime("%Y-%m-%dT%H:%M:%S") if event.end_date else None,
                'color': self.get_event_color(event.pupitre),
            }
            for event in events
        ]
        return json.dumps(events_list)

    def get_event_color(self, pupitre):
        return PUPITRES_COLORS.get(pupitre, '#D3D3D3')

    def get_next_events(self):
        today = datetime.today()
        return Evenement.objects.filter(start_date__gte=today).order_by('start_date').all()[
               0:self.how_many_events]

    def clean(self):
        if self.how_many_events < 1:
            self.how_many_events = 0

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


####                            #####
#       CHORISTES SECTIONS          #
####                            #####

class ChoristesIndexPage(Page):
    max_count = 1

    def get_children(self):
        return Choriste.objects.order_by('pupitre').all()


@register_snippet
class Choriste(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    pupitre = models.CharField(choices=PUPITRES_CHOICES, max_length=25, null=True, blank=True)
    mail = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('pupitre'),
        FieldPanel('mail'),
        FieldPanel('phone')
    ]

    def __str__(self):
        return self.name


@register_snippet
class Evenement(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_repetition = models.BooleanField(default=True)
    pupitre = models.CharField(choices=PUPITRES_CHOICES, max_length=25)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True)
    start_hour = models.TimeField(null=True)
    end_hour = models.TimeField(null=True)
    lieu = models.CharField(null=True, blank=True, max_length=250)
    adresse = models.CharField(null=True, blank=True, max_length=250)

    panels = [
        FieldPanel('name'),
        FieldPanel('is_repetition'),
        FieldPanel('description'),
        FieldPanel('pupitre'),
        FieldPanel('start_date'),
        FieldPanel('start_hour'),
        FieldPanel('end_hour'),
        FieldPanel('lieu'),
        FieldPanel('adresse'),
    ]

    def __str__(self):
        return f"{self.start_date.strftime('%d-%m')} // {self.name} - {self.pupitre} "
