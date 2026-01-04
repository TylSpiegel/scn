"""
Wagtail blocks for ContentPage.

This module provides:
- Basic content blocks (AlertBlock, TableBlock, EventChooserBlock, LinkBlock)
- Layout blocks (ColumnBlock, RowBlock, SectionBlock)
"""

from wagtail import blocks
from wagtail.blocks import (
    CharBlock,
    TextBlock,
    StructBlock,
    ChoiceBlock,
    RichTextBlock,
    StreamBlock,
    ListBlock,
)
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock


# =============================================================================
# CONTENT BLOCKS
# =============================================================================

class LinkBlock(StructBlock):
    """
    Button/link block for internal or external navigation.
    """
    link_type = ChoiceBlock(
        choices=[
            ('internal', 'Page interne'),
            ('external', 'URL externe'),
        ],
        icon='link',
        default='internal',
        label="Type de lien",
    )
    internal_page = blocks.PageChooserBlock(
        required=False,
        label="Page interne",
    )
    external_url = blocks.URLBlock(
        required=False,
        label="URL externe",
    )
    link_text = CharBlock(
        required=True,
        label="Texte du bouton",
    )
    style = ChoiceBlock(
        choices=[
            ('is-primary', 'Principal'),
            ('is-secondary', 'Secondaire'),
            ('is-outlined is-primary', 'Contour'),
        ],
        default='is-primary',
        label="Style",
    )
    open_in_new_tab = blocks.BooleanBlock(
        required=False,
        default=False,
        label="Ouvrir dans un nouvel onglet",
    )

    class Meta:
        icon = 'link'
        label = "Bouton"
        template = "blocks/button_block.html"

    def get_url(self, value):
        if value.get('link_type') == 'internal' and value.get('internal_page'):
            return value['internal_page'].url
        return value.get('external_url', '#')


class AlertBlock(StructBlock):
    """
    Alert/notification block with color variants.
    """
    color = ChoiceBlock(
        choices=[
            ('blue', 'Blue'),
            ('green', 'Green'),
            ('yellow', 'Yellow'),
            ('red', 'Red'),
        ],
        default='blue',
        label="Color",
    )
    title = CharBlock(
        required=False,
        label="Title",
        help_text="Optional title for the alert",
    )
    content = RichTextBlock(
        features=['bold', 'italic', 'link'],
        label="Content",
    )

    class Meta:
        template = "blocks/alert_block.html"
        icon = "warning"
        label = "Alert"


class TableBlock(StructBlock):
    """
    Table block with styling options.
    """
    table = WagtailTableBlock()
    first_row_is_header = blocks.BooleanBlock(
        required=False,
        default=True,
        label="First row is header",
    )
    first_col_is_header = blocks.BooleanBlock(
        required=False,
        default=False,
        label="First column is header",
    )
    style = ChoiceBlock(
        choices=[
            ('simple', 'Simple'),
            ('striped', 'Striped'),
            ('bordered', 'Bordered'),
        ],
        default='simple',
        label="Style",
    )

    class Meta:
        template = "blocks/table_block.html"
        icon = "table"
        label = "Table"


class EventChooserBlock(StructBlock):
    """
    Block to display a single event from the Evenement model.
    """
    event = SnippetChooserBlock(
        'choristes.Evenement',
        label="Event",
    )

    class Meta:
        template = "blocks/event_chooser_block.html"
        icon = "date"
        label = "Event"


class ImageBlock(StructBlock):
    """
    Image block with size options.
    """
    image = ImageChooserBlock(required=True)
    caption = CharBlock(
        required=False,
        help_text="Add a caption",
    )
    width = ChoiceBlock(
        choices=[
            ('160', 'Small'),
            ('320', 'Medium'),
            ('640', 'Large'),
            ('full', 'Full'),
        ],
        default='640',
        required=True,
        help_text="Select image size",
    )

    class Meta:
        template = "blocks/image_block.html"
        icon = "image"


# =============================================================================
# LAYOUT BLOCKS
# =============================================================================

class BaseContentStreamBlock(StreamBlock):
    """
    Base stream block containing all content types available in columns.
    """
    content = RichTextBlock(
        label="Rich Text",
    )
    button = LinkBlock()
    table = TableBlock()
    alert = AlertBlock()
    event = EventChooserBlock()

    class Meta:
        collapsed = True


class ColumnBlock(StructBlock):
    """
    A single column with content and alignment options.
    """
    alignment = ChoiceBlock(
        choices=[
            ('left', 'Left'),
            ('center', 'Center'),
            ('right', 'Right'),
        ],
        default='left',
        label="Alignment",
    )
    content = BaseContentStreamBlock(
        label="Content",
    )

    class Meta:
        template = "blocks/column_block.html"
        icon = "placeholder"
        label = "Column"


class RowBlock(StructBlock):
    """
    Row block with configurable column layout.
    """
    layout = ChoiceBlock(
        choices=[
            ('1', 'Full width'),
            ('1-1', 'Two columns (1/2 + 1/2)'),
            ('1-2', 'Two columns (1/3 + 2/3)'),
            ('2-1', 'Two columns (2/3 + 1/3)'),
            ('1-1-1', 'Three columns (equal)'),
        ],
        default='1',
        label="Layout",
    )
    columns = ListBlock(
        ColumnBlock(),
        label="Columns",
        collapsed=True,
    )

    class Meta:
        template = "blocks/row_block.html"
        icon = "grip"
        label = "Row"


class SectionBlock(StructBlock):
    """
    Section block with optional title containing multiple rows.
    This is the main container block for ContentPage.
    """
    title = CharBlock(
        required=False,
        label="Section title",
        help_text="Optional title displayed above the section",
    )
    rows = ListBlock(
        RowBlock(),
        label="Rows",
        collapsed=True,
    )

    class Meta:
        template = "blocks/section_block.html"
        icon = "doc-full"
        label = "Section"
