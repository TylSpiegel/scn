from django.db import models
from django.db.models import TextField
from django.forms import CharField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.blocks import RichTextBlock, StreamBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.admin.panels import FieldPanel

from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel

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


@register_setting
class StyleSettings(BaseGenericSetting):
    primary_color = ColorField(default='#FF0000')
    secondary_color = ColorField(default='#FF0000')
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Logo de votre site"
    )
    generic_theme = models.BooleanField(default=False)

    panels = [
        NativeColorPanel('primary_color'),
        NativeColorPanel('secondary_color'),
        FieldPanel('logo'),
        FieldPanel('generic_theme', help_text='Thème générique:')
    ]

    class Meta:
        verbose_name = 'Customisation'
