from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import TabbedInterface, ObjectList, MultiFieldPanel, FieldRowPanel
from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel


@register_setting
class ThemeSettings(BaseSiteSetting):
    primary_color = ColorField(default='#8a4d76', help_text="Boutons, liens, accents principaux")
    secondary_color = ColorField(default='#fa7c91', help_text="Survols, éléments secondaires")
    tertiary_color = ColorField(default='#3e8ed0', help_text="Badges, tags, informations")
    background_color = ColorField(default='#f5f5f5', help_text="Fond de page")
    text_color = ColorField(default='#2c3e50', help_text="Texte principal")
    text_muted_color = ColorField(default='#95a5a6', help_text="Texte secondaire")
    navbar_bg = ColorField(default='#8a4d76', help_text="Fond de la navigation")
    navbar_text = ColorField(default='#ffffff', help_text="Texte de navigation")
    navbar_hover_bg = ColorField(default='#6b3a5d', help_text="Fond au survol")

    edit_handler = TabbedInterface([
        ObjectList([
            MultiFieldPanel([
                FieldRowPanel([NativeColorPanel('primary_color'), NativeColorPanel('secondary_color')]),
                FieldRowPanel([NativeColorPanel('tertiary_color')]),
            ], heading="Couleurs principales"),
            MultiFieldPanel([
                FieldRowPanel([NativeColorPanel('background_color'), NativeColorPanel('text_color')]),
                FieldRowPanel([NativeColorPanel('text_muted_color')]),
            ], heading="Page & Texte"),
            MultiFieldPanel([
                FieldRowPanel([NativeColorPanel('navbar_bg'), NativeColorPanel('navbar_text')]),
                FieldRowPanel([NativeColorPanel('navbar_hover_bg')]),
            ], heading="Navigation"),
        ], heading='Thème'),
    ])

    class Meta:
        verbose_name = "Thème"
        verbose_name_plural = "Thème"
