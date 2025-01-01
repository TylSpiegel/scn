from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from ..blocks.audio_file_block import AudioDocumentBlock, AdditionalFilesBlock

class RepertoirePage(Page):
    """
    A page model for managing the choir's repertoire.
    Acts as a container/index for individual piece pages.
    """
    
    # Basic introduction text
    introduction = models.TextField(
        blank=True,
        help_text="A brief introduction to the repertoire",
        verbose_name="Introduction courte"
    )
    
    # Detailed description using rich text
    description = RichTextField(
        blank=True,
        help_text="Detailed description of the repertoire section",
        verbose_name="Description détaillée"
    )
    
    last_updated = models.DateTimeField(
        null=True,
        editable=False,
        help_text="Automatically updated when pieces are modified",
        verbose_name="Dernière mise à jour"
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("description"),
    ]

    # Page configuration
    subpage_types = ["music.pages.PiecePage"]  # Only allow PiecePage as children
    
    def get_context(self, request):
        """
        Add custom variables to template context.
        
        Args:
            request: The HTTP request object
            
        Returns:
            dict: Updated context dictionary
        """
        context = super().get_context(request)
        
        # Get all live pieces, ordered by title
        pieces = (
            PiecePage.objects
            .child_of(self)
            .live()
            .order_by('title')
        )
        
        # Add pieces to context
        context.update({
            'pieces': pieces,
        })
        
        return context
    
    def save(self, *args, **kwargs):
        """Update statistics before saving."""
        if self.pk:  # Only update stats if page already exists
            self.piece_count = (
                PiecePage.objects
                .child_of(self)
                .live()
                .count()
            )
            self.last_updated = timezone.now()
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Page Répertoire"
        verbose_name_plural = "Pages Répertoire"