"""
Wagtail page models for the home app.
"""

from django.db import models
from django.db.models import TextField

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    TabbedInterface,
    ObjectList,
    MultiFieldPanel,
    InlinePanel,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Orderable
from wagtail.blocks import RichTextBlock
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from .blocks import SectionBlock


class HomePage(Page):
    """
    Home page model.
    """
    name = TextField(help_text="Site title")
    header = TextField(help_text="Header")
    body = RichTextField(help_text="Page content")

    content_panels = Page.content_panels + [
        FieldPanel('name'),
        FieldPanel('header'),
        FieldPanel('body'),
    ]


class ContentPage(Page):
    """
    Generic content page with flexible block-based content.

    All content must be placed within sections (SectionBlock).
    Each section can have an optional title and contains multiple rows.
    """
    content = StreamField(
        [
            ('section', SectionBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("content"),
    ]

    class Meta:
        verbose_name = "Content Page"
        verbose_name_plural = "Content Pages"


class MenuItem(Orderable):
    """
    Individual menu item for navigation.
    """
    settings = ParentalKey(
        'StyleSettings',
        on_delete=models.CASCADE,
        related_name='menu_items'
    )

    title = models.CharField(
        max_length=50,
        verbose_name="Titre",
        help_text="Texte affiché dans le menu"
    )

    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Page interne",
        help_text="Lien vers une page du site"
    )

    link_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="URL externe",
        help_text="Ou lien vers une URL externe (si pas de page interne)"
    )

    open_in_new_tab = models.BooleanField(
        default=False,
        verbose_name="Ouvrir dans un nouvel onglet"
    )

    icon_class = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Classe d'icône",
        help_text="Classe FontAwesome (ex: fas fa-home)"
    )

    show_on_mobile = models.BooleanField(
        default=True,
        verbose_name="Afficher sur mobile"
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('open_in_new_tab'),
        FieldPanel('icon_class'),
        FieldPanel('show_on_mobile'),
    ]

    @property
    def url(self):
        if self.link_page:
            return self.link_page.url
        return self.link_url or '#'

    def __str__(self):
        return self.title


@register_setting
class StyleSettings(ClusterableModel, BaseSiteSetting):
    """
    Paramètres de style du site.
    """

    # ===============================
    # COULEURS PRINCIPALES
    # ===============================
    primary_color = ColorField(
        default='#8a4d76',
        help_text="Couleur principale - Boutons, liens, accents principaux"
    )
    secondary_color = ColorField(
        default='#fa7c91',
        help_text="Couleur secondaire - Survols, éléments secondaires"
    )
    tertiary_color = ColorField(
        default='#3e8ed0',
        help_text="Couleur tertiaire - Badges, tags, informations"
    )

    # ===============================
    # PAGE & TEXTE
    # ===============================
    background_color = ColorField(
        default='#f5f5f5',
        help_text="Fond de page"
    )
    text_color = ColorField(
        default='#2c3e50',
        help_text="Texte principal"
    )
    text_muted_color = ColorField(
        default='#95a5a6',
        help_text="Texte secondaire"
    )

    # ===============================
    # NAVIGATION
    # ===============================
    navbar_bg = ColorField(
        default='#8a4d76',
        help_text="Fond de la navigation"
    )
    navbar_text = ColorField(
        default='#ffffff',
        help_text="Texte de navigation"
    )
    navbar_hover_bg = ColorField(
        default='#6b3a5d',
        help_text="Fond au survol"
    )

    # ===============================
    # BRANDING
    # ===============================
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Logo",
        help_text="Logo du site affiché dans la navigation"
    )

    # ===============================
    # SÉCURITÉ / MOT DE PASSE
    # ===============================
    password = models.CharField(
        max_length=128,
        blank=True,
        default="",
        verbose_name="Mot de passe",
        help_text="Mot de passe pour protéger l'accès au site"
    )

    login_message = RichTextField(
        blank=True,
        default="",
        verbose_name="Message d'accueil",
        help_text="Message affiché sur la page de connexion"
    )

    # ===============================
    # PANELS D'ADMINISTRATION
    # ===============================
    security_panels = [
        MultiFieldPanel([
            FieldPanel('password'),
            FieldPanel('login_message'),
        ], heading="Protection par mot de passe"),
    ]

    navigation_panels = [
        MultiFieldPanel([
            FieldPanel('logo'),
        ], heading="Branding"),
        InlinePanel('menu_items', label="Liens du menu", heading="Menu de navigation"),
    ]

    theme_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                NativeColorPanel('primary_color'),
                NativeColorPanel('secondary_color'),
            ]),
            FieldRowPanel([
                NativeColorPanel('tertiary_color'),
            ]),
        ], heading="Couleurs principales"),
        MultiFieldPanel([
            FieldRowPanel([
                NativeColorPanel('background_color'),
                NativeColorPanel('text_color'),
            ]),
            FieldRowPanel([
                NativeColorPanel('text_muted_color'),
            ]),
        ], heading="Page & Texte"),
        MultiFieldPanel([
            FieldRowPanel([
                NativeColorPanel('navbar_bg'),
                NativeColorPanel('navbar_text'),
            ]),
            FieldRowPanel([
                NativeColorPanel('navbar_hover_bg'),
            ]),
        ], heading="Navigation"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(security_panels, heading='🔒 Sécurité'),
        ObjectList(navigation_panels, heading='🧭 Navigation'),
        ObjectList(theme_panels, heading='🎨 Thème'),
    ])

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"
