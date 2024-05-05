from wagtail.blocks import CharBlock, TextBlock, StructBlock, ChoiceBlock, RichTextBlock, StreamBlock, URLBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail import blocks

COLOR_CHOICES = [
    ('blue', 'Blue'),
    ('red', 'Red'),
]


class LinkBlock(blocks.StructBlock):
    link_type = blocks.ChoiceBlock(choices=[
        ('internal', 'Page interne'),
        ('external', 'URL externe'),
    ], icon='link', default='internal')
    internal_page = blocks.PageChooserBlock(required=False)
    external_url = blocks.URLBlock(required=False)
    link_text = blocks.CharBlock(required=True)

    class Meta:
        icon = 'link'
        template = "blocks/button_block.html"


class ImageBlock(StructBlock):
    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False, help_text="Ajouter une légende")
    width = ChoiceBlock(
        choices=[
            ('160', 'Petit'),
            ('320', 'Moyen'),
            ('640', 'Grand'),
            ('full', 'Max'),
        ],
        default='640',
        required=True,
        help_text="Sélectionnez la taille de l'image"
    )

    class Meta:
        template = "blocks/image_block.html"
        icon = "image"


class ColumnBlock(StreamBlock):
    content = RichTextBlock(required=False)
    button = LinkBlock(required=False)

    class Meta:
        icon = 'placeholder'
        label = 'Colonne'
        template = "blocks/column_block.html"


class MultiColumnBlock(StreamBlock):
    columns = ColumnBlock()

    class Meta:
        icon = 'placeholder'
        label = 'Section'
        template = 'blocks/multi_columns_block.html'
