
####                #####
#       MORCEAU         #
####                #####

class MorceauPage(Page):
    titre = models.CharField(max_length=250, null=True)
    compositeur = models.CharField(max_length=250, null=True, )
    descr = RichTextField(blank=True)
    traduction = RichTextField(blank=True)
    interpretation = RichTextField(blank=True)

    pdf = models.ForeignKey(
        Document,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    audios = StreamField([
        ('audios', AudioDocumentBlock()),
    ], null=True, blank=True, use_json_field=True)

    additional_files = StreamField([
        ('section', AdditionalFilesBlock()),
    ], null=True, blank=True, use_json_field=True)

    base_panels = Page.content_panels + [
        FieldPanel('titre'),
        FieldPanel('compositeur'),
        FieldPanel('descr'),
        FieldPanel('pdf'),
        FieldPanel('audios'),
        FieldPanel('additional_files')
    ]

    advanced_panels = [
        FieldPanel('traduction'),
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

