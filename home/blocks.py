from wagtail.blocks import CharBlock, TextBlock, StructBlock, ChoiceBlock, RichTextBlock,StreamBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock

COLOR_CHOICES = [
    ('blue', 'Blue'),
    ('red', 'Red'),
]

class ButtonBlock(StructBlock):

    button_text = CharBlock(
        required=False,
        help_text="Entrer une valeur ici annule le champ ci-dessus.",
    )

    """color = ChoiceBlock(
        default="blue",
        choices=COLOR_CHOICES,
        required=False
    )
    """
    color = 'blue'


    class Meta:
        template = "blocks/button_block.html"


class ImageBlock(StructBlock):
    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False, help_text="Ajouter une légende")

    class Meta:
        template = "blocks/image_block.html"
        icon = "image"

class ColumnBlock(StreamBlock):

    content = RichTextBlock(required=False)
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