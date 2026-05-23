from django.db import models
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField


@register_setting
class SecuritySettings(BaseSiteSetting):
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

    panels = [
        MultiFieldPanel([
            FieldPanel('password'),
            FieldPanel('login_message'),
        ], heading="Protection par mot de passe"),
    ]

    class Meta:
        verbose_name = "Sécurité"
        verbose_name_plural = "Sécurité"
