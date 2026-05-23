from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock


class EventBlock(blocks.StructBlock):
    event = SnippetChooserBlock('community.Event', label="Événement")
    extra_content = blocks.RichTextBlock(
        required=False,
        label="Contenu supplémentaire",
    )

    class Meta:
        icon = 'date'
        label = 'Événement'
        template = 'blocks/event_block.html'


class PieceBlock(SnippetChooserBlock):
    def __init__(self, *args, **kwargs):
        super().__init__('music.Piece', *args, **kwargs)

    def get_template(self, context=None):
        return 'blocks/piece_block.html'

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        ctx['piece'] = value
        return ctx

    class Meta:
        icon = 'media'
        label = 'Morceau'
