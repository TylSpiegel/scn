import json
import sys

from datetime import timedelta

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
from ..blocks import AudioDocumentBlock, AdditionalFilesBlock


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
