from django.db import models
from django.core.validators import RegexValidator
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel
from django.core.exceptions import ValidationError

@register_snippet
class Section(models.Model):
    """
    Model representing a choir section (e.g., Soprano, Alto, etc.)
    with customizable name and color.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du pupitre",
        help_text="Nom de la section (ex: Soprano, Alto...)"
    )
    
    color = ColorField(
        unique=True,
        verbose_name="Couleur",
        help_text="Couleur associée à la section"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description optionnelle de la section"
    )

    def clean(self):
        """Validate the model data."""
        super().clean()
        
        # Ensure name is properly formatted
        if self.name:
            # Capitalize first letter
            self.name = self.name.strip().capitalize()
            
            # Check for invalid characters
            if any(char in self.name for char in '<>:"/\\|?*'):
                raise ValidationError({
                    'name': "Le nom contient des caractères non autorisés"
                })

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Pupitre"
        verbose_name_plural = "Pupitres"
        ordering = ['name']

    panels = [
        FieldPanel('name'),
        NativeColorPanel('color'),
        FieldPanel('description'),
    ]