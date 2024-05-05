from django.db import models
from django.db.models import TextField
from django.forms import CharField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.blocks import RichTextBlock, StreamBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList

from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel

from .blocks import LinkBlock, ImageBlock, MultiColumnBlock


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
    # THEME
    primary_color = ColorField(default='#FF0000')
    secondary_color = ColorField(default='#FF0000')
    third_color = ColorField(default='#FF0000')

    generic_theme = models.BooleanField(default=False)

    theme_panel = [
        NativeColorPanel('primary_color'),
        NativeColorPanel('secondary_color'),
        NativeColorPanel('third_color'),
    ]
    # BRANDING
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Logo de votre site"
    )

    branding_panel = [
        FieldPanel('logo'),
        FieldPanel('generic_theme', help_text='Thème générique:')
    ]

    # PASSWORD

    password_message = RichTextField(
        help_text="Le texte qui sera affiché sur la page de demande de mot de passe.",
        default="",
    )

    image_password = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Image qui sera affichée sur la page de demande de mot de passe."
    )

    password_panel = [
        FieldPanel('password_message'),
        FieldPanel('image_password')
    ]

    #####

    edit_handler = TabbedInterface([
        ObjectList(theme_panel, heading='Thème'),
        ObjectList(branding_panel, heading='Branding'),
        ObjectList(password_panel, heading='Password'),
    ])

    class Meta:
        verbose_name = 'Customisation'
