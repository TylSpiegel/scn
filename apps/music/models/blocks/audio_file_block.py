from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel


class AudioBlock(blocks.StructBlock):
   section = models.ForeignKey(
       'Section',
       verbose_name="Pupitre",
       on_delete=models.CASCADE
   )
   custom_section = blocks.CharBlock(
       max_length=30,
       required=False,
       verbose_name="Pupitre personnalisé",
       help_text="Définir un pupitre différent"
   )
   audio_file = DocumentChooserBlock(
       required=False, 
       verbose_name="Fichier audio",
       #TODO : add valid formats in help text
       help_text=""
   )
   notes = blocks.CharBlock(
       required=False,
       max_length=255,
       verbose_name="Notes",
       help_text="Commentaires sur l'enregistrement"
   )

   def clean(self, value):
       cleaned_data = super().clean(value)
       if not cleaned_data.get('section') and not cleaned_data.get('custom_section'):
           raise ValidationError('Un pupitre doit être sélectionné ou défini')
       return cleaned_data

   class Meta:
       icon = "media"
       template = "music/blocks/audio.html"
       verbose_name = "Fichier audio"
       form_classname = "audio-block"
       edit_handler = MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('section', classname="col4"),
                FieldPanel('custom_section', classname="col8"),
            ]),
            FieldPanel('audio_file'),
            FieldPanel('notes'),
        ], heading="Ajout d'un fichier audio")


from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from typing import Any, Dict, Optional
import mimetypes
import os

class AudioBlock(blocks.StructBlock):
    """
    A StreamField block for audio files with section assignment.
    Allows uploading audio files and associating them with specific choir sections.
    """
    
    section = models.ForeignKey(
        'Section',
        verbose_name="Pupitre",
        on_delete=models.CASCADE,
        help_text="Select the choir section for this audio"
    )
    
    custom_section = blocks.CharBlock(
        max_length=30,
        required=False,
        verbose_name="Pupitre personnalisé",
        help_text="Define a custom section if needed. This will override the standard section selection."
    )
    
    audio_file = DocumentChooserBlock(
        required=False,
        verbose_name="Fichier audio",
        help_text="Supported formats: MP3, WAV, OGG, M4A (max 50MB)"
    )
    
    notes = blocks.CharBlock(
        required=False,
        max_length=255,
        verbose_name="Notes",
        help_text="Add comments about the recording (optional)"
    )

    def validate_audio_file(self, document: Any) -> None:
        """
        Validates the uploaded audio file for format and size constraints.
        
        Args:
            document: The uploaded document object
            
        Raises:
            ValidationError: If the file doesn't meet the requirements
        """
        if not document or not document.file:
            return

        # Supported audio formats
        ALLOWED_AUDIO_EXTENSIONS = ['.mp3', '.wav', '.ogg', '.m4a']
        ALLOWED_MIME_TYPES = [
            'audio/mpeg', 'audio/wav', 'audio/ogg', 
            'audio/mp4', 'audio/x-m4a'
        ]
        
        # Size limits
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        MIN_FILE_SIZE = 1024  # 1KB

        filename = document.filename.lower()
        extension = os.path.splitext(filename)[1]
        
        # Check file extension
        if extension not in ALLOWED_AUDIO_EXTENSIONS:
            raise ValidationError({
                'audio_file': f"Format non supporté. Formats acceptés : {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
            })
        
        # Check file size
        if document.file.size > MAX_FILE_SIZE:
            raise ValidationError({
                'audio_file': f"Le fichier est trop volumineux. Taille maximum : {filesizeformat(MAX_FILE_SIZE)}"
            })
            
        if document.file.size < MIN_FILE_SIZE:
            raise ValidationError({
                'audio_file': "Le fichier semble être vide ou corrompu."
            })
            
        # Check MIME type
        mime_type = mimetypes.guess_type(filename)[0]
        if mime_type not in ALLOWED_MIME_TYPES:
            raise ValidationError({
                'audio_file': "Le type de fichier ne correspond pas à un format audio supporté."
            })
        
        # Try to read the file header
        try:
            document.file.open()
            document.file.read(1024)
            document.file.close()
        except Exception as e:
            raise ValidationError({
                'audio_file': "Le fichier semble être corrompu ou illisible."
            })

    def clean(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs validation on the block's data.
        
        Args:
            value: Dictionary containing the block's data
            
        Returns:
            Dict[str, Any]: Cleaned data if valid
            
        Raises:
            ValidationError: If validation fails
        """
        cleaned_data = super().clean(value)
        
        # Validate section selection
        if not cleaned_data.get('section') and not cleaned_data.get('custom_section'):
            raise ValidationError('Un pupitre doit être sélectionné ou défini')
        
        # Validate audio file if present
        if audio_file := cleaned_data.get('audio_file'):
            self.validate_audio_file(audio_file)
            
        # Validate notes length and content
        if notes := cleaned_data.get('notes'):
            if len(notes) > 255:
                raise ValidationError({
                    'notes': "Les notes sont trop longues (maximum 255 caractères)"
                })
        
        return cleaned_data

    class Meta:
        icon = "media"
        template = "music/blocks/audio_file_block.html"
        verbose_name = "Fichier audio"
        form_classname = "audio-block"
        help_text = "Add an audio file with section assignment"
        
        # Panel configuration
        edit_handler = MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('section', classname="col4"),
                FieldPanel('custom_section', classname="col8"),
            ]),
            FieldPanel('audio_file'),
            FieldPanel('notes'),
        ], heading="Ajout d'un fichier audio")