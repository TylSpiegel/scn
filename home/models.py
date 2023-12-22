from django.db import models
from django.db.models import TextField
from django.forms import CharField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.blocks import RichTextBlock, StreamBlock

from .blocks import ButtonBlock, ImageBlock, MultiColumnBlock


class HomePage(Page):
	name = TextField(help_text="Titre du site")
	header = TextField(help_text="En-tête")
	body = RichTextField(help_text="Contenu de la page")

	content_panels = Page.content_panels + [
		FieldPanel('name'),
		FieldPanel('header'),
		FieldPanel('body'),
	]


class ContentPage(Page):
	content = StreamField([
		('contenu', RichTextBlock()),
		('image', ImageBlock()),
		('colonnes', MultiColumnBlock())
	], null=True, blank=True, use_json_field=True)

	content_panels = Page.content_panels + [
		FieldPanel("content"),
	]
