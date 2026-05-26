from django.db import models
from wagtail.models import Orderable
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel


@register_setting
class NavigationSettings(BaseSiteSetting, ClusterableModel):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Logo",
        help_text="Logo affiché dans la navbar (recommandé : 150x50px)"
    )

    site_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom du site",
        help_text="Affiché à côté du logo ou seul si pas de logo"
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('logo'),
            FieldPanel('site_name'),
        ], heading="Identité du site"),
        InlinePanel('menu_items', label="Liens du menu", heading="Menu de navigation"),
    ]

    class Meta:
        verbose_name = "Navigation"
        verbose_name_plural = "Navigation"


class MenuItem(Orderable):
    navigation = ParentalKey(
        NavigationSettings,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )

    title = models.CharField(max_length=50, verbose_name="Titre")

    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Page interne",
    )

    link_url = models.URLField(blank=True, verbose_name="URL externe")

    open_in_new_tab = models.BooleanField(default=False, verbose_name="Ouvrir dans un nouvel onglet")

    icon_class = models.CharField(max_length=50, blank=True, verbose_name="Classe d'icône")

    show_on_mobile = models.BooleanField(default=True, verbose_name="Afficher sur mobile")

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
