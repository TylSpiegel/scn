from datetime import date

from django.db import models
from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from modelcluster.fields import ParentalKey

from apps.content.blocks import EventBlock, PieceBlock


class ContentSection(Orderable):
    page = ParentalKey(
        'ContentPage',
        on_delete=models.CASCADE,
        related_name='sections'
    )
    title = models.CharField(max_length=255, verbose_name="Titre")
    date = models.DateField(default=date.today, verbose_name="Date")
    body = RichTextField(verbose_name="Contenu", blank=True)
    references = StreamField(
        [
            ('event', EventBlock()),
            ('piece', PieceBlock()),
        ],
        blank=True,
        null=True,
        use_json_field=True,
        verbose_name="Références",
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('date'),
        FieldPanel('body'),
        FieldPanel('references'),
    ]

    def __str__(self):
        return self.title


class ContentPage(Page):
    content_panels = Page.content_panels + [
        InlinePanel('sections', label="Sections"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['sections'] = self.sections.all()
        return context

    class Meta:
        verbose_name = "Page de contenu"
        verbose_name_plural = "Pages de contenu"


class HomePage(Page):
    name = models.TextField(help_text="Site title")
    header = models.TextField(help_text="Header")
    body = RichTextField(help_text="Page content")

    content_panels = Page.content_panels + [
        FieldPanel('name'),
        FieldPanel('header'),
        FieldPanel('body'),
    ]

    class Meta:
        verbose_name = "Page d'accueil"
        verbose_name_plural = "Pages d'accueil"
