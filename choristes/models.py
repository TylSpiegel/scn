from django.db import models
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
    max_count = 1

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
    max_count = 1

    # FIELDS
    calendrier_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Le calendrier en format image"
    )
    comment = RichTextField(
        blank=True,
        help_text="Un espace pour ajouter des commentaires : les changements récents, les prochaines dates..."
    )
    content_panels = Page.content_panels + [
        FieldPanel("calendrier_image"),
        FieldPanel('comment'),
    ]


####                            #####
#       CHORISTES SECTIONS          #
####                            #####

class ChoristesIndexPage(Page):
    max_count = 1

    def get_children(self):
        return Choriste.objects.order_by('pupitre').all()


@register_snippet
class Choriste(models.Model):
    name = models.CharField(max_length=255)
    pupitre = models.CharField(choices=PUPITRES_CHOICES, max_length=25)
    mail = models.EmailField()
    phone = models.CharField(max_length=12)

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
    name = models.CharField(max_length=255)
    description = models.TextField()
    repetition = models.BooleanField(default=True)
    pupitre = models.CharField(choices=PUPITRES_CHOICES, max_length=25)
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    start_hour = models.TimeField(null=True)
    end_hour = models.TimeField(null=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('pupitre'),
        FieldPanel('repetition'),
        FieldPanel('start_date')
    ]

    def __str__(self):
        return f"{self.name} - {self.pupitre} - {self.start_date.strftime('%d-%m')}"
