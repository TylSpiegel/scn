from django.db import models
from django.db.models import TextField

from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList, MultiFieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Orderable
from wagtail.blocks import RichTextBlock
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting

from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

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


class MenuItem(Orderable):
    """Individual menu item for navigation."""

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
    Paramètres de style et couleurs du site.
    """

    # ===============================
    # COULEURS PRINCIPALES
    # ===============================
    primary_color = ColorField(
        default='#8a4d76',
        help_text="🎨 Couleur principale - Boutons, liens, accents principaux"
    )
    secondary_color = ColorField(
        default='#fa7c91',
        help_text="🎨 Couleur secondaire - Survols, éléments secondaires"
    )
    tertiary_color = ColorField(
        default='#3e8ed0',
        help_text="🎨 Couleur tertiaire - Badges, tags, informations"
    )

    # ===============================
    # BLOCS DE CONTENU
    # ===============================
    block_header_bg = ColorField(
        default='#8a4d76',
        help_text="📦 Fond des en-têtes de blocs"
    )
    block_header_text = ColorField(
        default='#ffffff',
        help_text="📦 Texte des en-têtes de blocs"
    )

    # ===============================
    # TITRES
    # ===============================
    title_h1_color = ColorField(
        default='#2c3e50',
        help_text="🎯 Titres principaux (h1)"
    )
    title_h2_color = ColorField(
        default='#34495e',
        help_text="🎯 Sous-titres (h2)"
    )
    title_h3_color = ColorField(
        default='#7f8c8d',
        help_text="🎯 Titres de sections (h3)"
    )

    # ===============================
    # PAGE & TEXTE
    # ===============================
    background_color = ColorField(
        default='#f5f5f5',
        help_text="📄 Fond de page"
    )
    text_color = ColorField(
        default='#2c3e50',
        help_text="📄 Texte principal"
    )
    text_muted_color = ColorField(
        default='#95a5a6',
        help_text="📄 Texte secondaire"
    )

    # ===============================
    # NAVIGATION
    # ===============================
    navbar_bg = ColorField(
        default='#8a4d76',
        help_text="🔗 Fond de la navigation"
    )
    navbar_text = ColorField(
        default='#ffffff',
        help_text="🔗 Texte de navigation"
    )
    navbar_hover_bg = ColorField(
        default='#6b3a5d',
        help_text="🔗 Fond au survol"
    )

    # ===============================
    # ÉVÉNEMENTS (Calendrier)
    # ===============================
    event_rehearsal_color = ColorField(
        default='#3e8ed0',
        help_text="🎪 Répétitions"
    )
    event_concert_color = ColorField(
        default='#fa7c91',
        help_text="🎪 Concerts"
    )

    # ===============================
    # BRANDING & NAVIGATION
    # ===============================
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Logo de votre site"
    )

    site_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Nom du site",
        help_text="Affiché à côté du logo dans la navbar"
    )

    # ===============================
    # PASSWORD
    # ===============================
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

    # ===============================
    # PANELS D'ADMINISTRATION
    # ===============================
    colors_main_panel = [
        MultiFieldPanel([
            NativeColorPanel('primary_color'),
            NativeColorPanel('secondary_color'),
            NativeColorPanel('tertiary_color'),
        ], heading="🎨 Couleurs Principales"),
    ]

    colors_blocks_panel = [
        MultiFieldPanel([
            NativeColorPanel('block_header_bg'),
            NativeColorPanel('block_header_text'),
        ], heading="📦 Blocs de Contenu"),
    ]

    colors_titles_panel = [
        MultiFieldPanel([
            NativeColorPanel('title_h1_color'),
            NativeColorPanel('title_h2_color'),
            NativeColorPanel('title_h3_color'),
        ], heading="🎯 Titres"),
    ]

    colors_page_panel = [
        MultiFieldPanel([
            NativeColorPanel('background_color'),
            NativeColorPanel('text_color'),
            NativeColorPanel('text_muted_color'),
        ], heading="📄 Page & Texte"),
    ]

    colors_nav_panel = [
        MultiFieldPanel([
            NativeColorPanel('navbar_bg'),
            NativeColorPanel('navbar_text'),
            NativeColorPanel('navbar_hover_bg'),
        ], heading="🔗 Couleurs Navigation"),
    ]

    colors_events_panel = [
        MultiFieldPanel([
            NativeColorPanel('event_rehearsal_color'),
            NativeColorPanel('event_concert_color'),
        ], heading="🎪 Événements"),
    ]

    branding_panel = [
        FieldPanel('logo'),
        FieldPanel('site_name'),
    ]

    navigation_panel = [
        InlinePanel('menu_items', label="Liens du menu"),
    ]

    password_panel = [
        FieldPanel('password_message'),
        FieldPanel('image_password')
    ]

    edit_handler = TabbedInterface([
        ObjectList(colors_main_panel + colors_blocks_panel, heading='🎨 Couleurs - Base'),
        ObjectList(colors_titles_panel + colors_page_panel, heading='📝 Couleurs - Typographie'),
        ObjectList(colors_nav_panel + colors_events_panel, heading='🔗 Couleurs - Événements'),
        ObjectList(branding_panel, heading='🖼️ Branding'),
        ObjectList(navigation_panel, heading='📍 Menu'),
        ObjectList(password_panel, heading='🔒 Protection'),
    ])

    class Meta:
        verbose_name = 'Customisation du Site'
        verbose_name_plural = 'Customisation du Site'
