

class PollBlock(blocks.StructBlock):
    """
    A block for choosing and displaying a poll.
    
    Features:
    - Selects from existing Poll snippets
    - Handles response collection
    - Shows/hides results based on poll configuration
    - Updates in real-time using AlpineJS
    """
    
    poll = SnippetChooserBlock('interactions.Poll')
    
    class Meta:
        template = 'blocks/poll_block.html'
        icon = 'list-ul'
        label = _('Sondage')
        help_text = _('Intégrez un sondage avec réponses oui/non/peut-être')