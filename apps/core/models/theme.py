from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList

from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel

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
