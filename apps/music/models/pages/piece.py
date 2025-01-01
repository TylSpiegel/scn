from django.db import models
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList
from wagtail.fields import RichTextField, StreamField 
from wagtail.models import Page
from wagtail.documents.models import Document
from ..blocks.audio_file_block import AudioDocumentBlock, AdditionalFilesBlock

####                #####
#       MORCEAU         #
####                #####
class PiecePage(Page):
    name = models.CharField("Titre", max_length=250)  
    composer = models.CharField("Compositeur", max_length=250)
    description = RichTextField("Description", blank=True)
    translation = RichTextField("Traduction", blank=True)
    interpretation = RichTextField("Interprétation", blank=True)
    
    score = models.ForeignKey(
        Document,
        verbose_name="Partition",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    audio_files = StreamField([
        ('audio', AudioBlock()),
    ], verbose_name="Fichiers audio", blank=True, use_json_field=True)

    additional_content = StreamField([
        ('files_section', AdditionalContentBlock()),
    ], verbose_name="Contenus additionnels", blank=True, use_json_field=True)
    

    base_panels = Page.content_panels + [
        FieldPanel('name'),
        FieldPanel('composer'),
        FieldPanel('description'),
        FieldPanel('score'),
        FieldPanel('audio_files'),
        FieldPanel('additional_content')
    ]
    
    advanced_panels = [
        FieldPanel('translation'),
    ]

    interpretation_panels = [
        FieldPanel('interpretation'),
    ]
    
    edit_handler = TabbedInterface([
        ObjectList(base_panels, heading='Infos de base'),
        ObjectList(advanced_panels, heading='Texte, traduction et interprétation'),
        ObjectList(interpretation_panels, heading='Indications musicales'),
        ObjectList(Page.promote_panels, heading='Routing'),
    ])

    def get_context(self, request):
        context = super().get_context(request)
        context['audios'] = sorted(self.audios, key=lambda x: x.value['pupitre'])
        return context

    parent_page_types = ["MorceauIndexPage"]
    subpage_types = []
	
    def clean(self):
        if not self.title:
            self.title = self.name
        super().clean()

    def __str__(self):
        return f"{self.name} - {self.composer}"

    class Meta:
        verbose_name = "Morceau"
        verbose_name_plural = "Morceaux"
        ordering = ['name']
        indexes = [
            models.Index(fields=['composer']),
            models.Index(fields=['name'])
        ]

        search_fields = Page.search_fields + [
            index.SearchField('name'),
            index.SearchField('composer'),
            index.SearchField('description'),
            index.FilterField('composer')
        ]

        parent_page_types = ['RepertoirePage']
        subpage_types = []

