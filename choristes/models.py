from django.db import models
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from wagtail.admin.panels import TabbedInterface, ObjectList
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

from .blocks import MorceauBlock, AudioDocumentBlock, AdditionalFilesBlock

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


"""
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
	max_count = 1

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
"""

####                            #####
#       CHORISTES SECTIONS          #
####                            #####
