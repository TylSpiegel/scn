from django.db import models
from wagtail.models import Page
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField

from apps.content.blocks import PRIVATE_BLOCK_TYPES, ImageBlock, SectionBlock


def _section_label(section):
    title = section.value["title"]
    return f"la section « {title} »" if title else "une section sans titre"


def private_content_in(body):
    """Blocs du corps d'une page qui ne doivent pas apparaître sur une page publique."""
    found = []
    for section in body:
        if section.block_type != "section":
            continue  # images hors section : jamais privées
        for block in section.value["content"]:
            if block.block_type in PRIVATE_BLOCK_TYPES:
                found.append(f"« {block.block.label} » dans {_section_label(section)}")
            elif (
                block.block_type == "form"
                and block.value
                and block.value.get_view_restrictions().exists()
            ):
                found.append(
                    f"le formulaire privé « {block.value.title} » dans {_section_label(section)}"
                )
            elif (
                block.block_type == "document"
                and block.value
                and block.value.collection.get_view_restrictions().exists()
            ):
                found.append(
                    f"le document privé « {block.value.title} » dans {_section_label(section)}"
                )
    return found


class ContentPageForm(WagtailAdminPageForm):
    """
    Garde-fou : une page sans restriction de confidentialité (propre ou héritée) est publique,
    elle ne peut donc pas afficher d'événement, de morceau ni de formulaire rangé côté privé.
    """

    def clean(self):
        cleaned_data = super().clean()
        body = cleaned_data.get("body")
        if not body or self._is_restricted():
            return cleaned_data

        found = private_content_in(body)
        if found:
            self.add_error(
                None,
                (
                    "Cette page est publique : elle ne peut pas afficher de contenu privé. "
                    f"À retirer : {' ; '.join(found)}."
                ),
            )
        return cleaned_data

    def _is_restricted(self):
        page = self.instance if self.instance.pk else self.parent_page
        return page is not None and page.get_view_restrictions().exists()


class ContentPage(Page):
    TEMPLATE_CHOICES = [
        ("standard", "Standard"),
        ("banner", "Bannière"),
        ("full", "Pleine largeur"),
    ]

    template_variant = models.CharField(
        max_length=20,
        choices=TEMPLATE_CHOICES,
        default="standard",
        verbose_name="Gabarit",
        help_text="Standard : colonne centrée. Bannière : en-tête pleine largeur. "
        "Pleine largeur : sections sur bandeaux colorés.",
    )
    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Image de bannière",
        help_text="Utilisée par le gabarit « Bannière » et comme image de partage sur les réseaux sociaux.",
    )
    body = StreamField(
        [("section", SectionBlock()), ("image", ImageBlock())],
        blank=True,
        verbose_name="Contenu",
        help_text="Des sections, et des images entre elles si besoin.",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("template_variant"),
                FieldPanel("banner_image"),
            ],
            heading="Mise en page",
        ),
        FieldPanel("body"),
    ]

    base_form_class = ContentPageForm

    def get_template(self, request, *args, **kwargs):
        variant = self.template_variant
        if variant not in dict(self.TEMPLATE_CHOICES):
            variant = "standard"
        return f"content/content_page_{variant}.html"

    class Meta:
        verbose_name = "Page de contenu"
        verbose_name_plural = "Pages de contenu"


class HomePage(Page):
    name = models.TextField(help_text="Site title")
    header = models.TextField(help_text="Header")
    body = RichTextField(help_text="Page content")

    content_panels = Page.content_panels + [
        FieldPanel("name"),
        FieldPanel("header"),
        FieldPanel("body"),
    ]

    parent_page_types = ["wagtailcore.Page"]

    class Meta:
        verbose_name = "Page d'accueil"
        verbose_name_plural = "Pages d'accueil"
