from django.db import models
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField


@register_setting
class SecuritySettings(BaseSiteSetting):
    login_message = RichTextField(
        blank=True,
        default="",
        verbose_name="Message d'accueil",
        help_text="Message affiché au-dessus du formulaire de mot de passe. "
        "Le mot de passe lui-même se règle avec le bouton « Confidentialité » de la page racine.",
    )
    allow_indexing = models.BooleanField(
        default=False,
        verbose_name="Autoriser l'indexation",
        help_text="Laisser les moteurs de recherche indexer ce site (sitemap, robots.txt). "
        "À n'activer que sur le site public.",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("login_message"),
            ],
            heading="Protection par mot de passe",
        ),
        MultiFieldPanel(
            [
                FieldPanel("allow_indexing"),
            ],
            heading="Référencement",
        ),
    ]

    class Meta:
        verbose_name = "Sécurité"
        verbose_name_plural = "Sécurité"
