from wagtail.fields import RichTextField
from wagtail import blocks

class EnhancedRichTextField(RichTextField):
   def __init__(self, *args, **kwargs):
       kwargs.setdefault('features', [
           'h2', 'h3', 'bold', 'italic', 'link',
           'ol', 'ul', 'hr', 'document-link', 'image',
           'embed', 'code', 'superscript', 'subscript', 'strikethrough'
       ])
       super().__init__(*args, **kwargs)