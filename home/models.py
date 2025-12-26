from django.db import models
from django.db.models import TextField

from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.blocks import RichTextBlock

from wagtail.contrib.settings.models import BaseGenericSetting, register_setting

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
    """
    Paramètres de style et couleurs du site.
    
    NOMENCLATURE DES COULEURS:
    
    🎨 COULEURS PRINCIPALES:
    - primary_color: Couleur principale (boutons, liens actifs, accents)
    - secondary_color: Couleur secondaire (survols, éléments secondaires)
    - tertiary_color: Couleur tertiaire (badges, tags, éléments d'information)
    
    📦 BLOCS DE CONTENU:
    - block_header_bg: Fond des en-têtes de blocs (sections colorées des cartes)
    - block_header_text: Texte des en-têtes de blocs (doit contraster avec block_header_bg)
    
    🎯 TITRES:
    - title_h1_color: Couleur des titres principaux (h1)
    - title_h2_color: Couleur des sous-titres (h2)
    - title_h3_color: Couleur des titres de sections (h3)
    
    📄 PAGE:
    - background_color: Couleur de fond général de la page
    - text_color: Couleur du texte principal
    - text_muted_color: Couleur du texte secondaire/grisé
    
    🔗 NAVIGATION:
    - navbar_bg: Fond de la barre de navigation
    - navbar_text: Texte de la navigation
    - navbar_hover_bg: Fond au survol des liens de navigation
    
    🎪 ÉVÉNEMENTS (Calendrier):
    - event_rehearsal_color: Couleur pour les répétitions
    - event_concert_color: Couleur pour les concerts
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
        help_text="📦 Fond des en-têtes de blocs - Sections colorées des cartes de contenu"
    )
    block_header_text = ColorField(
        default='#ffffff',
        help_text="📦 Texte des en-têtes de blocs - Doit contraster avec le fond"
    )
    
    # ===============================
    # TITRES
    # ===============================
    title_h1_color = ColorField(
        default='#2c3e50',
        help_text="🎯 Titres principaux (h1) - Titres de pages"
    )
    title_h2_color = ColorField(
        default='#34495e',
        help_text="🎯 Sous-titres (h2) - Titres de sections majeures"
    )
    title_h3_color = ColorField(
        default='#7f8c8d',
        help_text="🎯 Titres de sections (h3) - Sous-sections"
    )
    
    # ===============================
    # PAGE & TEXTE
    # ===============================
    background_color = ColorField(
        default='#f5f5f5',
        help_text="📄 Fond de page - Couleur de fond général du site"
    )
    text_color = ColorField(
        default='#2c3e50',
        help_text="📄 Texte principal - Couleur du contenu textuel"
    )
    text_muted_color = ColorField(
        default='#95a5a6',
        help_text="📄 Texte secondaire - Texte grisé, moins important"
    )
    
    # ===============================
    # NAVIGATION
    # ===============================
    navbar_bg = ColorField(
        default='#8a4d76',
        help_text="🔗 Fond de la navigation - Barre de menu principale"
    )
    navbar_text = ColorField(
        default='#ffffff',
        help_text="🔗 Texte de navigation - Liens du menu"
    )
    navbar_hover_bg = ColorField(
        default='#6b3a5d',
        help_text="🔗 Fond au survol - Couleur quand on survole un lien du menu"
    )
    
    # ===============================
    # ÉVÉNEMENTS (Calendrier)
    # ===============================
    event_rehearsal_color = ColorField(
        default='#3e8ed0',
        help_text="🎪 Répétitions - Couleur pour les événements de type répétition"
    )
    event_concert_color = ColorField(
        default='#fa7c91',
        help_text="🎪 Concerts - Couleur pour les événements de type concert"
    )
    
    # ===============================
    # THÈME GÉNÉRIQUE
    # ===============================
    generic_theme = models.BooleanField(
        default=False,
        help_text="Utiliser le thème générique simple"
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
        ], heading="🔗 Navigation"),
    ]
    
    colors_events_panel = [
        MultiFieldPanel([
            NativeColorPanel('event_rehearsal_color'),
            NativeColorPanel('event_concert_color'),
        ], heading="🎪 Événements"),
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
        FieldPanel('generic_theme'),
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

    edit_handler = TabbedInterface([
        ObjectList(colors_main_panel + colors_blocks_panel, heading='🎨 Couleurs - Base'),
        ObjectList(colors_titles_panel + colors_page_panel, heading='📝 Couleurs - Typographie'),
        ObjectList(colors_nav_panel + colors_events_panel, heading='🔗 Couleurs - Navigation'),
        ObjectList(branding_panel, heading='🖼️ Branding'),
        ObjectList(password_panel, heading='🔒 Protection'),
    ])

    default_auto_field = 'django.db.models.BigAutoField'
    
    class Meta:
        verbose_name = 'Customisation du Site'
        verbose_name_plural = 'Customisation du Site'
