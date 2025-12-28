import json
import sys

from datetime import timedelta, datetime, time

from django.db import models
from django.utils import timezone
from django.db.models.functions import ExtractMonth, ExtractYear
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django import forms
from wagtail import blocks

from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import TabbedInterface, ObjectList, MultiFieldPanel, FieldRowPanel
from wagtail.admin.panels import (
    FieldPanel,
)
from wagtail.documents.models import Document
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from .blocks import AudioDocumentBlock, AdditionalFilesBlock

from wagtail.models import ClusterableModel
from wagtail.admin.panels import InlinePanel
from modelcluster.fields import ParentalKey, ParentalManyToManyField

PUPITRES_CHOICES = (
    ('Tutti', 'Tutti'),
    ('Soprano', 'Soprano'),
    ('Alto', 'Alto'),
    ('Mezzo-alto', 'Mezzo-alto'),
    ('Mezzo-soprano', 'Mezzo-soprano'),
    ('Ténor', 'Ténor'),
    ('Basse', 'Basse'),
    ('Autre', 'Autre'),
)

PUPITRES_COLORS = {
    'Tutti': '#007BFF',
    'Soprano': '#DC3545',
    'Mezzo-soprano': '#E91E63',
    'Alto': '#FFC107',
    'Mezzo-alto': '#FF9800',
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
class TimecodeBlock(blocks.StructBlock):
    """Block pour un timecode individuel."""
    timecode = blocks.CharBlock(
        help_text="Format mm:ss, ex: 02:45",
        label="Timecode",
        validators=[
            RegexValidator(
                regex=r'^([0-5][0-9]):([0-5][0-9])$',
                message="Le format doit être mm:ss (ex: 02:45)"
            )
        ]
    )
    texte = blocks.TextBlock(label="Texte associé")

    class Meta:
        template = 'blocks/timecode_block.html'
        icon = 'time'


class MorceauPage(Page):
    titre = models.CharField(max_length=250, null=True)
    compositeur = models.CharField(max_length=250, null=True)
    descr = RichTextField(blank=True)
    traduction = RichTextField(blank=True)
    interpretation = RichTextField(blank=True)

    activer_timecodes = models.BooleanField(
        default=False,
        verbose_name="Activer les timecodes",
        help_text="Cochez pour activer la fonctionnalité de timecodes"
    )

    timecodes = StreamField([
        ('timecode', TimecodeBlock()),
    ], null=True, blank=True, use_json_field=True,
        verbose_name="Timecodes avec annotations")

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
        FieldPanel('activer_timecodes'),
        FieldPanel('timecodes'),
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

        # Trier les timecodes par valeur numérique
        if self.activer_timecodes:
            sorted_timecodes = []
            for block in self.timecodes:
                if block.block_type == 'timecode':
                    tc_parts = block.value['timecode'].split(':')
                    # Convertir en secondes pour le tri
                    tc_seconds = int(tc_parts[0]) * 60 + int(tc_parts[1])
                    sorted_timecodes.append((tc_seconds, block))

            sorted_timecodes.sort(key=lambda x: x[0])
            context['sorted_timecodes'] = [item[1] for item in sorted_timecodes]

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
        events_list = []
        
        for event in events:
            # Construire le datetime de début
            start_datetime = datetime.combine(event.start_date, event.start_time or time(0, 0))
            
            # Construire le datetime de fin
            end_date = event.end_date if event.end_date else event.start_date
            end_datetime = None
            if event.end_time:
                end_datetime = datetime.combine(end_date, event.end_time)
            
            events_list.append({
                'title': event.name,
                'start': start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                'end': end_datetime.strftime("%Y-%m-%dT%H:%M:%S") if end_datetime else None,
                'location': event.lieu if event.lieu else '',
                'color': '#3e8ed0' if event.is_repetition else '#fa7c91',
            })
        
        return json.dumps(events_list)

    def get_event_color(self, pupitre):
        return PUPITRES_COLORS.get(pupitre, '#D3D3D3')

    def get_next_events(self):
        today = datetime.today().date()
        # Filtrer sur start_date car c'est un DateField
        upcoming = Evenement.objects.filter(start_date__gte=today).order_by('start_date', 'start_time')
        return upcoming[0:self.how_many_events]

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

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Créer un dictionnaire pour l'ordre des pupitres
        pupitre_order = {pupitre[0]: idx for idx, pupitre in enumerate(PUPITRES_CHOICES)}

        # Récupérer tous les choristes et les trier
        choristes = Choriste.objects.all()

        # Trier d'abord par l'ordre des pupitres, puis par nom
        choristes_sorted = sorted(
            choristes,
            key=lambda c: (
                pupitre_order.get(c.pupitre, 999),  # 999 pour les pupitres non définis
                c.name
            )
        )

        context['choristes'] = choristes_sorted

        return context


@register_snippet
class Choriste(ClusterableModel):
    active = models.BooleanField(default=False, verbose_name="Actif")
    name = models.CharField(max_length=255, null=False, blank=False,
                            verbose_name="Nom", help_text="Nom du choriste")
    pupitre = models.CharField(choices=PUPITRES_CHOICES, max_length=25,
                               null=True, blank=True, verbose_name="Pupitre")
    mail = models.EmailField(null=True, blank=True, verbose_name="Email")
    phone = models.CharField(max_length=15, null=True, blank=True,
                             verbose_name="Téléphone")
    birthdate = models.DateField(null=True, blank=True,
                                 verbose_name="Date de naissance")
    choir_functions = ParentalManyToManyField(
        'ChoirRole',
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
    street = models.CharField(max_length=255, null=False, blank=False,
                              verbose_name="Rue", help_text="Rue")
    zip_code = models.CharField(max_length=10, null=False, blank=False,
                                verbose_name="Code postal")
    city = models.CharField(max_length=255, null=False, blank=False,
                            verbose_name="Localité")

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


@register_snippet
class ChoirRole(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False,
                            verbose_name="Nom", help_text="Nom de la fonction")
    description = models.TextField(null=True, blank=True,
                                   verbose_name="Description")

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


@register_snippet
class Evenement(models.Model):
    name = models.CharField(
        max_length=255, 
        verbose_name="Nom de l'événement"
    )
    description = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Description"
    )
    is_repetition = models.BooleanField(
        default=True,
        verbose_name="Répétition"
    )
    pupitre = models.CharField(
        choices=PUPITRES_CHOICES, 
        max_length=25,
        verbose_name="Pupitre"
    )
    
    # Dates
    start_date = models.DateField(
        verbose_name="Date de début",
        help_text="Date de début de l'événement (obligatoire)"
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Date de fin",
        help_text="Date de fin (si différente de la date de début)"
    )
    
    # Heures
    time_tbd = models.BooleanField(
        default=False,
        verbose_name="Heure à déterminer",
        help_text="Cochez si l'heure n'est pas encore fixée"
    )
    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de début",
        help_text="Heure de début (laissez vide si heure à déterminer)"
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de fin",
        help_text="Heure de fin (optionnel)"
    )
    
    # Lieu
    lieu = models.CharField(
        null=True, 
        blank=True, 
        max_length=250,
        verbose_name="Lieu"
    )
    adresse = models.CharField(
        null=True, 
        blank=True, 
        max_length=250,
        verbose_name="Adresse"
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('is_repetition'),
        FieldPanel('pupitre'),
        FieldPanel('description'),
        
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
        ], heading="📅 Dates et heures"),
        
        MultiFieldPanel([
            FieldPanel('lieu'),
            FieldPanel('adresse'),
        ], heading="📍 Localisation"),
    ]

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['start_date', 'start_time']

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Si end_date n'est pas définie, la mettre égale à start_date
        if not self.end_date:
            self.end_date = self.start_date
        
        # Vérifier que end_date >= start_date
        if self.end_date < self.start_date:
            raise ValidationError({
                'end_date': 'La date de fin ne peut pas être antérieure à la date de début.'
            })
        
        # Si time_tbd est coché, les heures doivent être vides
        if self.time_tbd:
            if self.start_time or self.end_time:
                raise ValidationError({
                    'time_tbd': 'Si "Heure à déterminer" est coché, les heures doivent être vides.'
                })
        
        # Si time_tbd n'est pas coché, avertir si pas d'heure de début
        if not self.time_tbd and not self.start_time:
            # Cette validation pourrait être transformée en warning dans l'admin
            pass
        
        # Si une heure de fin est définie, il faut une heure de début
        if self.end_time and not self.start_time:
            raise ValidationError({
                'end_time': 'Vous devez définir une heure de début si vous définissez une heure de fin.'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        date_str = self.start_date.strftime('%d-%m')
        time_str = ""
        
        if self.time_tbd:
            time_str = " (heure TBD)"
        elif self.start_time:
            time_str = f" {self.start_time.strftime('%H:%M')}"
        
        return f"{date_str}{time_str} // {self.name} - {self.pupitre}"
    
    @property
    def display_time(self):
        """Retourne l'affichage formaté de l'heure"""
        if self.time_tbd:
            return "Heure à déterminer"
        elif self.start_time:
            if self.end_time:
                return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
            return self.start_time.strftime('%H:%M')
        return ""
    
    @property
    def datetime_start(self):
        """Retourne un datetime combinant date et heure de début"""
        if self.start_time:
            return datetime.combine(self.start_date, self.start_time)
        return datetime.combine(self.start_date, time(0, 0))
    
    @property
    def datetime_end(self):
        """Retourne un datetime combinant date et heure de fin"""
        end_date = self.end_date if self.end_date else self.start_date
        if self.end_time:
            return datetime.combine(end_date, self.end_time)
        return None


####                            #####
#       NAVIGATION SETTINGS         #
####                            #####

from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.images.models import Image


@register_setting
class NavigationSettings(BaseSiteSetting, ClusterableModel):
    """Site navigation settings - logo and menu links."""
    
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Logo",
        help_text="Logo affiche dans la navbar (recommande: 150x50px)"
    )
    
    site_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom du site",
        help_text="Affiche a cote du logo ou seul si pas de logo"
    )
    
    panels = [
        MultiFieldPanel([
            FieldPanel('logo'),
            FieldPanel('site_name'),
        ], heading="Identite du site"),
        InlinePanel('menu_items', label="Liens du menu", heading="Menu de navigation"),
    ]

    class Meta:
        verbose_name = "Navigation"
        verbose_name_plural = "Navigation"


class MenuItem(Orderable):
    """Individual menu item."""
    
    navigation = ParentalKey(
        NavigationSettings,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    
    title = models.CharField(
        max_length=50,
        verbose_name="Titre",
        help_text="Texte affiche dans le menu"
    )
    
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Page interne",
        help_text="Lien vers une page du site"
    )
    
    link_url = models.URLField(
        blank=True,
        verbose_name="URL externe",
        help_text="Ou lien vers une URL externe (si pas de page interne)"
    )
    
    open_in_new_tab = models.BooleanField(
        default=False,
        verbose_name="Ouvrir dans un nouvel onglet"
    )
    
    icon_class = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Classe d'icone",
        help_text="Classe FontAwesome (ex: fas fa-home)"
    )
    
    show_on_mobile = models.BooleanField(
        default=True,
        verbose_name="Afficher sur mobile"
    )
    
    panels = [
        FieldPanel('title'),
        FieldPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('open_in_new_tab'),
        FieldPanel('icon_class'),
        FieldPanel('show_on_mobile'),
    ]
    
    @property
    def url(self):
        if self.link_page:
            return self.link_page.url
        return self.link_url or '#'
    
    def __str__(self):
        return self.title
