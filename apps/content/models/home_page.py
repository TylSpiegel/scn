from django.db import models
from django.db.models import TextField
from django.forms import CharField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page


class HomePage(Page):
    name = TextField(help_text="Titre du site")
    header = TextField(help_text="En-tête")
    body = RichTextField(help_text="Contenu de la page")

    content_panels = Page.content_panels + [
        FieldPanel('name'),
        FieldPanel('header'),
        FieldPanel('body'),
    ]
    """
    #TODO: Allow to choose pinned pages here (instead of choosing page per page)
    #TODO: Enhance the content
        - Allow some widgetisation :    
            - Show X coming events + description
            - Show a photo ?
            - Display a custom text
    """  
