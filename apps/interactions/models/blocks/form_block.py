

class FormBlock(blocks.SnipperChooserBlock):
    """
    A block for choosing and displaying a custom form.
    
    Features:
    - Selects from existing CustomForm entities
    - Handles form rendering and submission
    - Processes responses according to form configuration
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            target_model='interactions.CustomForm',
            template='blocks/form_block.html',
            **kwargs
        )