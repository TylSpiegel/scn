from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from apps.interaction.blocks import FormBlock


RICH_TEXT_FEATURES = [
    "h2",
    "h3",
    "h4",
    "bold",
    "italic",
    "ol",
    "ul",
    "blockquote",
    "hr",
    "link",
    "document-link",
    "image",
    "embed",
]


class EventBlock(blocks.StructBlock):
    event = SnippetChooserBlock("community.Event", label="Événement")
    extra_content = blocks.RichTextBlock(
        required=False,
        label="Contenu supplémentaire",
    )

    class Meta:
        icon = "date"
        label = "Événement"
        template = "blocks/event_block.html"


class PieceBlock(blocks.PageChooserBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, page_type="music.Piece", **kwargs)

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        ctx["piece"] = value.specific if value else None
        return ctx

    class Meta:
        icon = "media"
        label = "Morceau"
        template = "blocks/piece_block.html"


# ---- Mini-composants ------------------------------------------------------
# Deux ou trois champs au plus, rendus avec les couleurs de la palette.

LAYOUT_GROUP = "Mise en forme"
MEDIA_GROUP = "Médias"
CHOIR_GROUP = "Contenu du chœur"


class ButtonBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=60, label="Libellé")
    page = blocks.PageChooserBlock(required=False, label="Page du site")
    url = blocks.URLBlock(required=False, label="ou adresse externe")
    style = blocks.ChoiceBlock(
        choices=[("filled", "Plein"), ("outlined", "Contour")],
        default="filled",
        label="Style",
    )

    def clean(self, value):
        value = super().clean(value)
        if bool(value.get("page")) == bool(value.get("url")):
            raise blocks.StructBlockValidationError(
                block_errors={"page": ValidationError("Choisissez une page du site ou une adresse externe.")}
            )
        return value

    class Meta:
        icon = "link"
        label = "Bouton"
        template = "blocks/button_block.html"


class CalloutBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(features=["bold", "italic", "link"], label="Texte")
    tone = blocks.ChoiceBlock(
        choices=[("info", "Information"), ("important", "Important")],
        default="info",
        label="Ton",
    )

    class Meta:
        icon = "warning"
        label = "Encadré"
        template = "blocks/callout_block.html"


class QuoteBlock(blocks.StructBlock):
    text = blocks.TextBlock(label="Citation")
    author = blocks.CharBlock(required=False, max_length=120, label="Auteur")

    class Meta:
        icon = "openquote"
        label = "Citation"
        template = "blocks/quote_block.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Image")
    caption = blocks.CharBlock(required=False, max_length=255, label="Légende")

    class Meta:
        icon = "image"
        label = "Image"
        template = "blocks/image_block.html"


class PracticalInfoBlock(blocks.StructBlock):
    ICONS = {
        "date": "fa-calendar-days",
        "time": "fa-clock",
        "place": "fa-location-dot",
        "price": "fa-ticket",
        "duration": "fa-hourglass-half",
        "info": "fa-circle-info",
    }
    kind = blocks.ChoiceBlock(
        choices=[
            ("date", "Date"),
            ("time", "Heure"),
            ("place", "Lieu"),
            ("price", "Prix / entrée"),
            ("duration", "Durée"),
            ("info", "Information"),
        ],
        default="info",
        label="Type",
    )
    text = blocks.CharBlock(max_length=255, label="Texte")

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        ctx["icon"] = self.ICONS.get(value["kind"], self.ICONS["info"])
        ctx["kind_label"] = dict(self.child_blocks["kind"].field.choices).get(value["kind"], "")
        return ctx

    class Meta:
        icon = "pick"
        label = "Info pratique"
        template = "blocks/practical_info_block.html"


class KeyFigureBlock(blocks.StructBlock):
    number = blocks.CharBlock(max_length=20, label="Chiffre", help_text="Ex. : 40, 2×/an, 2023")
    label = blocks.CharBlock(max_length=60, label="Libellé", help_text="Ex. : choristes")

    class Meta:
        icon = "order"
        label = "Chiffre clé"
        template = "blocks/key_figure_block.html"


class DocumentBlock(DocumentChooserBlock):
    class Meta:
        icon = "doc-full"
        label = "Document"
        template = "blocks/document_block.html"


class SeparatorBlock(blocks.StaticBlock):
    class Meta:
        icon = "horizontalrule"
        label = "Séparateur"
        admin_text = "Petit trait centré entre deux contenus."
        template = "blocks/separator_block.html"


class SpacerBlock(blocks.ChoiceBlock):
    choices = [("small", "Petit"), ("medium", "Moyen"), ("large", "Grand")]

    class Meta:
        icon = "arrows-up-down"
        label = "Espace"
        default = "medium"
        template = "blocks/spacer_block.html"


# Blocs qui affichent des données privées : refusés sur une page publique.
# Les formulaires et documents ne le sont que s'ils sont rangés côté privé (voir pages.py).
PRIVATE_BLOCK_TYPES = ("event", "piece")


class SectionContentBlock(blocks.StreamBlock):
    text = blocks.RichTextBlock(features=RICH_TEXT_FEATURES, label="Texte")
    button = ButtonBlock(group=LAYOUT_GROUP)
    callout = CalloutBlock(group=LAYOUT_GROUP)
    quote = QuoteBlock(group=LAYOUT_GROUP)
    practical_info = PracticalInfoBlock(group=LAYOUT_GROUP)
    key_figure = KeyFigureBlock(group=LAYOUT_GROUP)
    separator = SeparatorBlock(group=LAYOUT_GROUP)
    spacer = SpacerBlock(group=LAYOUT_GROUP)
    image = ImageBlock(group=MEDIA_GROUP)
    table = TableBlock(
        group=MEDIA_GROUP,
        label="Tableau",
        template="blocks/table_block.html",
        table_options={"startRows": 3, "startCols": 3, "autoColumnSize": False},
    )
    document = DocumentBlock(group=MEDIA_GROUP)
    event = EventBlock(group=CHOIR_GROUP)
    piece = PieceBlock(group=CHOIR_GROUP)
    form = FormBlock(group=CHOIR_GROUP)


class SectionBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=False, label="Titre")
    date = blocks.DateBlock(required=False, label="Date")
    content = SectionContentBlock(required=False, label="Contenu")

    class Meta:
        icon = "doc-full"
        label = "Section"
        template = "blocks/section_block.html"
