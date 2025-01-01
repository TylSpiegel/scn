from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from typing import Any, Dict
import os

class FileBlock(blocks.StructBlock):
    name = blocks.CharBlock(
        required=True,
        verbose_name="Nom du fichier",
        help_text="Donnez un nom descriptif au fichier",
        min_length=3,
        max_length=100
    )
    
    documents = blocks.ListBlock(
        DocumentChooserBlock(
            verbose_name="Sélection du fichier",
            help_text="Sélectionnez un ou plusieurs fichiers"
        ),
        max_num=10,  # Limite maximum de fichiers
    )
    
    notes = blocks.CharBlock(
        required=False,
        max_length=255,
        verbose_name="Notes sur le fichier",
        help_text="Ajoutez des notes ou commentaires sur le fichier (optionnel)"
    )

    def get_file_type(self, filename: str) -> str:
        """Détermine le type de fichier basé sur l'extension."""
        SUPPORTED_EXTENSIONS = {
            'audio': ['.mp3', '.wav', '.ogg', '.m4a'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.md'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            'archive': ['.zip', '.rar', '.7z'],
            'spreadsheet': ['.xls', '.xlsx', '.csv'],
        }
        
        ext = os.path.splitext(filename.lower())[1]
        for type_name, extensions in SUPPORTED_EXTENSIONS.items():
            if ext in extensions:
                return type_name
        return 'other'

    def clean(self, value: Dict[str, Any]) -> Dict[str, Any]:
        cleaned_data = super().clean(value)
        
        if 'documents' in cleaned_data:
            total_size = 0
            MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100MB total
            MAX_SINGLE_FILE_SIZE = 20 * 1024 * 1024  # 20MB par fichier
            
            # Liste des extensions interdites
            FORBIDDEN_EXTENSIONS = ['.exe', '.bat', '.cmd', '.sh', '.php', '.js']
            
            for doc in cleaned_data['documents']:
                if doc:
                    if not doc.file:
                        raise ValidationError({
                            'documents': f"Le fichier {doc.filename} est manquant ou corrompu."
                        })
                    
                    # Vérification de la taille du fichier individuel
                    if doc.file.size > MAX_SINGLE_FILE_SIZE:
                        raise ValidationError({
                            'documents': f"Le fichier {doc.filename} dépasse la taille maximale autorisée de {filesizeformat(MAX_SINGLE_FILE_SIZE)}."
                        })
                    
                    # Vérification des extensions interdites
                    ext = os.path.splitext(doc.filename.lower())[1]
                    if ext in FORBIDDEN_EXTENSIONS:
                        raise ValidationError({
                            'documents': f"Le type de fichier {ext} n'est pas autorisé pour des raisons de sécurité."
                        })
                    
                    total_size += doc.file.size
                    
                    # Vérification basique du contenu du fichier
                    try:
                        doc.file.open()
                        # Lire les premiers octets pour vérifier si le fichier est lisible
                        doc.file.read(1024)
                        doc.file.close()
                    except Exception as e:
                        raise ValidationError({
                            'documents': f"Le fichier {doc.filename} semble être corrompu ou illisible."
                        })
            
            # Vérification de la taille totale
            if total_size > MAX_TOTAL_SIZE:
                raise ValidationError({
                    'documents': f"La taille totale des fichiers ({filesizeformat(total_size)}) dépasse la limite autorisée de {filesizeformat(MAX_TOTAL_SIZE)}."
                })

        # Validation du nom
        if 'name' in cleaned_data:
            if any(char in cleaned_data['name'] for char in '<>:"/\\|?*'):
                raise ValidationError({
                    'name': "Le nom contient des caractères non autorisés (< > : \" / \\ | ? *)"
                })

        return cleaned_data

    class Meta:
        icon = "doc-full"
        template = "music/blocks/file_block.html"
        verbose_name = "Ajout d'un fichier"
        help_text = "Ajouter un ou plusieurs fichiers avec description"