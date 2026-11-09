from wagtail import blocks
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


# Blocs qui affichent des données privées : refusés sur une page publique.
PRIVATE_BLOCK_TYPES = ("event", "piece")


class SectionContentBlock(blocks.StreamBlock):
    text = blocks.RichTextBlock(features=RICH_TEXT_FEATURES, label="Texte")
    event = EventBlock()
    piece = PieceBlock()
    form = FormBlock()


class SectionBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=False, label="Titre")
    date = blocks.DateBlock(required=False, label="Date")
    content = SectionContentBlock(required=False, label="Contenu")

    class Meta:
        icon = "doc-full"
        label = "Section"
        template = "blocks/section_block.html"
