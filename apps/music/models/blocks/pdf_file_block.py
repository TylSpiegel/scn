from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from typing import Any, Dict

class PdfFileBlock(blocks.StructBlock):
    name = blocks.CharBlock(
        required=True,
        verbose_name="Nom du fichier",
        help_text="Donnez un nom descriptif au fichier"
    )
    documents = blocks.ListBlock(
        DocumentChooserBlock(
            verbose_name="Sélection du pdf",
            help_text="Sélectionnez un ou plusieurs fichiers PDF"
        )
    )
    notes = blocks.CharBlock(
        required=False,
        max_length=255,
        verbose_name="Notes sur le fichier",
        help_text="Ajoutez des notes ou commentaires sur le fichier (optionnel)"
    )

    def clean(self, value: Dict[str, Any]) -> Dict[str, Any]:
        cleaned_data = super().clean(value)
        
        # Validate documents
        if 'documents' in cleaned_data:
            for doc in cleaned_data['documents']:
                if doc:
                    # Check if document exists
                    if not doc.file:
                        raise ValidationError({
                            'documents': "Le fichier est manquant ou corrompu."
                        })
                    
                    # Check file extension
                    filename = doc.filename.lower()
                    if not filename.endswith('.pdf'):
                        raise ValidationError({
                            'documents': f"Le fichier {filename} n'est pas un PDF. Seuls les fichiers PDF sont acceptés."
                        })
                    
                    # Check file size (max 20MB)
                    max_size = 20 * 1024 * 1024  # 20MB in bytes
                    if doc.file.size > max_size:
                        raise ValidationError({
                            'documents': f"Le fichier {filename} est trop volumineux. La taille maximale est de 20MB."
                        })

        # Validate name length
        if 'name' in cleaned_data and len(cleaned_data['name']) < 3:
            raise ValidationError({
                'name': "Le nom du fichier doit contenir au moins 3 caractères."
            })

        return cleaned_data

    class Meta:
        icon = "doc-full"
        template = "music/blocks/pdf_file_block.html"
        verbose_name = "Ajout d'un fichier"
        help_text = "Ajouter un ou plusieurs fichiers PDF avec description"