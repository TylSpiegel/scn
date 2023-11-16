from django.db import models

from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
    MultiFieldPanel,
    MultipleChooserPanel,
    InlinePanel
)

from wagtail.documents.models import Document
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail import blocks

from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import Image

from .blocks import MorceauBlock, AudioDocumentBlock

from django.core.serializers import serialize
import json
from datetime import date, datetime

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

    parent_page_types = ["MorceauIndexPage"]
    subpage_types = []


class MorceauPage(Page):

    titre = models.CharField(max_length=250, null=True)
    compositeur = models.CharField(max_length=250, null=True,)
    descr = RichTextField(blank=True)
    traduction = RichTextField(blank=True)

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

    content_panels = Page.content_panels + [
        FieldPanel('titre'),
        FieldPanel('compositeur'),
        FieldPanel('descr'),
        FieldPanel('pdf'),
        FieldPanel('audios'),
        FieldPanel('traduction'),
    ]
    def documents(self):
        """
        Returns the RecipePage's related people. Again note that we are using
        the ParentalKey's related_name from the RecipePersonRelationship model
        to access these objects. This allows us to access the Person objects
        with a loop on the template. If we tried to access the recipe_person_
        relationship directly we'd print `recipe.RecipePersonRelationship.None`
        """
        # Only return authors that are not in draft
        return [
            n.person
            for n in self.recipe_person_relationship.filter(
                person__live=True
            ).select_related("person")
        ]

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

    @classmethod
    def can_create_at(cls, parent):
        return 1

class CalendrierPage(Page):

    introduction = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel('image'),
    ]
    subpage_types = ["CalendrierEventPage", "CalendrierPublicEventPage"]
    parent_page_types = ["ChoristesIndexPage"]
    def children(self):
        return self.get_children().specific().live()

    def get_events_json(self):
        events = CalendrierEventPage.objects.live()
        public_events = CalendrierPublicEventPage.objects.live()
        formatted_events = []
        for event in events:
            current_event = {
                'title': event.title,
                'start': event.date.isoformat()
                    if isinstance(event.date, date)
                    else event.date
            }
            formatted_events.append(current_event)
        for public_event in public_events:
            current_event = {
                'title': public_event.title,
                'start': public_event.date.isoformat()
                    if isinstance(public_event.date, date)
                    else public_event.date
            }
            formatted_events.append(current_event)
        return json.dumps(formatted_events)

    def get_context(self, request):
        context = super().get_context(request)
        context['events_json'] = self.get_events_json()
        return context

class CalendrierEventPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
    ]
    parent_page_types = ["CalendrierPage"]
    subpage_types = []

class CalendrierPublicEventPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
    ]
    parent_page_types = ["CalendrierPage"]
    subpage_types = []

class ChoristesPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
    ]


class ChoristesIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]
