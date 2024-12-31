from django.db import models
from django.db.models import TextField
from django.forms import CharField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page


class ContentPage(Page):
    content = StreamField([
        ('contenu', RichTextBlock()),
        ('image', ImageBlock()),
        ('colonnes', MultiColumnBlock())
    ], null=True, blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("content"),
    ]
"""
#TODO: Add column/grid into RichTextField

"""