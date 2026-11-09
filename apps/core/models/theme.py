from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import format_html, format_html_join
from wagtail.admin.panels import FieldPanel, FieldRowPanel, HelpPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail_color_panel.edit_handlers import NativeColorPanel
from wagtail_color_panel.fields import ColorField

PALETTE_SLOTS = 5

# Contraste minimal (WCAG) en dessous duquel l'enregistrement est refusé.
MIN_TEXT_CONTRAST = 4.5
MIN_UI_CONTRAST = 3

COLOR_FIELDS = [
    "primary_color",
    "secondary_color",
    "tertiary_color",
    "background_color",
    "text_color",
    "text_muted_color",
    "navbar_bg",
    "navbar_text",
    "navbar_hover_bg",
]


def _luminance(hex_color):
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(color_a, color_b):
    lighter, darker = sorted((_luminance(color_a), _luminance(color_b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class Palette(models.Model):
    """
    Une des 5 palettes de l'instance (emplacements fixes : on les modifie et les renomme,
    on n'en ajoute ni n'en supprime). Chaque site choisit la sienne dans « Thème ».
    """

    slot = models.PositiveSmallIntegerField(
        unique=True, editable=False, verbose_name="Emplacement"
    )
    name = models.CharField(max_length=50, verbose_name="Nom")

    primary_color = ColorField(
        default="#8a4d76",
        verbose_name="Couleur principale",
        help_text="Boutons, liens, bannières, en-têtes de page et cadres. Le texte posé dessus est blanc.",
    )
    secondary_color = ColorField(
        default="#fa7c91",
        verbose_name="Couleur d'accent",
        help_text="Survol des liens et boutons, séparateurs, concerts dans le calendrier.",
    )
    tertiary_color = ColorField(
        default="#3e8ed0",
        verbose_name="Couleur complémentaire",
        help_text="Badges, répétitions dans le calendrier, une bande sur deux du gabarit « Pleine largeur ».",
    )
    background_color = ColorField(
        default="#f5f5f5",
        verbose_name="Fond de page",
        help_text="Derrière les cartes et le contenu. Une teinte claire est recommandée.",
    )
    text_color = ColorField(
        default="#2c3e50",
        verbose_name="Texte",
        help_text="Texte courant et titres de section.",
    )
    text_muted_color = ColorField(
        default="#95a5a6",
        verbose_name="Texte discret",
        help_text="Dates, légendes et informations secondaires.",
    )
    navbar_follows_primary = models.BooleanField(
        default=True,
        verbose_name="Barre de navigation aux couleurs principales",
        help_text="Fond = couleur principale, texte blanc, survol un peu plus foncé. "
        "Décochez pour choisir les trois couleurs ci-dessous.",
    )
    navbar_bg = ColorField(
        default="#8a4d76",
        verbose_name="Fond de la barre",
        help_text="Utilisé seulement si la case ci-dessus est décochée.",
    )
    navbar_text = ColorField(
        default="#ffffff",
        verbose_name="Texte de la barre",
        help_text="Utilisé seulement si la case ci-dessus est décochée.",
    )
    navbar_hover_bg = ColorField(
        default="#6b3a5d",
        verbose_name="Fond au survol",
        help_text="Utilisé seulement si la case ci-dessus est décochée.",
    )

    panels = [
        FieldPanel("name"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        NativeColorPanel("primary_color"),
                        NativeColorPanel("secondary_color"),
                    ]
                ),
                FieldRowPanel([NativeColorPanel("tertiary_color")]),
            ],
            heading="Couleurs du site",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        NativeColorPanel("background_color"),
                        NativeColorPanel("text_color"),
                    ]
                ),
                FieldRowPanel([NativeColorPanel("text_muted_color")]),
            ],
            heading="Fond et texte",
        ),
        MultiFieldPanel(
            [
                FieldPanel("navbar_follows_primary"),
                FieldRowPanel(
                    [
                        NativeColorPanel("navbar_bg"),
                        NativeColorPanel("navbar_text"),
                        NativeColorPanel("navbar_hover_bg"),
                    ]
                ),
            ],
            heading="Barre de navigation",
        ),
    ]

    class Meta:
        verbose_name = "Palette"
        verbose_name_plural = "Palettes"
        ordering = ["slot"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        errors = {}
        checks = [
            (
                "text_color",
                self.text_color,
                self.background_color,
                MIN_TEXT_CONTRAST,
                "Le texte est peu lisible sur le fond de page",
            ),
            (
                "primary_color",
                "#ffffff",
                self.primary_color,
                MIN_UI_CONTRAST,
                "Le texte blanc des boutons et bannières est peu lisible sur cette couleur principale",
            ),
        ]
        if not self.navbar_follows_primary:
            checks.append(
                (
                    "navbar_text",
                    self.navbar_text,
                    self.navbar_bg,
                    MIN_UI_CONTRAST,
                    "Le texte de la barre de navigation est peu lisible sur son fond",
                )
            )

        for field, foreground, background, minimum, message in checks:
            try:
                ratio = contrast_ratio(foreground, background)
            except (TypeError, ValueError):
                continue  # couleur invalide : déjà signalée par le validateur du champ
            if ratio < minimum:
                errors[field] = (
                    f"{message} (contraste {ratio:.1f}:1, minimum {minimum}:1)."
                )
        if errors:
            raise ValidationError(errors)

    @property
    def navbar_colors(self):
        """Couleurs effectives de la barre de navigation (fond, texte, survol)."""
        if self.navbar_follows_primary:
            return (
                self.primary_color,
                "#ffffff",
                "color-mix(in srgb, var(--primary-color) 80%, black)",
            )
        return self.navbar_bg, self.navbar_text, self.navbar_hover_bg

    def swatches(self):
        colors = [
            self.primary_color,
            self.secondary_color,
            self.tertiary_color,
            self.background_color,
            self.text_color,
        ]
        return format_html(
            '<span style="display:inline-flex;gap:3px">{}</span>',
            format_html_join(
                "",
                '<span title="{0}" style="display:inline-block;width:1.4rem;height:1.4rem;'
                'border-radius:4px;border:1px solid rgba(0,0,0,.15);background:{0}"></span>',
                ((color,) for color in colors),
            ),
        )

    swatches.short_description = "Couleurs"

    def used_by(self):
        sites = [str(theme.site) for theme in self.themes.select_related("site")]
        return ", ".join(sites) or "—"

    used_by.short_description = "Utilisée par"


@register_setting
class ThemeSettings(BaseSiteSetting):
    palette = models.ForeignKey(
        Palette,
        null=True,
        on_delete=models.SET_NULL,
        related_name="themes",
        verbose_name="Palette",
    )

    panels = [
        HelpPanel(
            content="<p>Chaque site (public, privé) choisit sa palette : sélectionnez le site en haut "
            "de la page. Les cinq palettes se modifient et se renomment dans "
            '<a href="/admin/snippets/core/palette/">Paramètres › Palettes</a>.</p>'
        ),
        FieldPanel("palette", widget=forms.RadioSelect),
    ]

    class Meta:
        verbose_name = "Thème"
        verbose_name_plural = "Thème"

    @property
    def colors(self):
        """Palette active ; à défaut la première, à défaut les couleurs par défaut."""
        return self.palette or Palette.objects.first() or Palette()
