from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock


class AudioDocumentBlock(blocks.StructBlock):
    # Vous pouvez ajouter des attributs supplémentaires si nécessaire
    audio = DocumentChooserBlock(required=False, help_text="Sélectionnez un fichier audio")

    class Meta:
        icon = "media"
        template = "blocks/audio_file.html"


class MorceauBlock(blocks.StructBlock):
    titre = blocks.CharBlock(required=True, max_length=255, help_text="Entrez le titre")
    texte = blocks.TextBlock(required=True, help_text="Entrez le texte principal")
    document_pdf = DocumentChooserBlock(required=True, help_text="Sélectionnez un document PDF")

    documents_audio = blocks.ListBlock(
        AudioDocumentBlock(),
        min_num=0,
        max_num=4,
        help_text="Ajoutez entre 1 et 4 fichiers audio"
    )

    champs_texte_supplementaires = blocks.StreamBlock(
        [('texte_supplementaire', blocks.TextBlock())],
        help_text="Ajoutez un nombre indéterminé de champs texte",
        required=False
    )
    class Meta:
        icon = "form"
        template = "blocks/morceau.html"