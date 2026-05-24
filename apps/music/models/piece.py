from django.db import models

from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel, TabbedInterface, ObjectList
from wagtail.documents.models import Document
from wagtail.fields import RichTextField, StreamField
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase

from apps.music.blocks import AudioDocumentBlock, AdditionalFilesBlock, TimecodeBlock


class PieceIndexPage(Page):
    template = 'music/piece_index_page.html'

    introduction = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]

    subpage_types = ['music.Piece']

    def get_context(self, request):
        context = super().get_context(request)
        context['pieces'] = Piece.objects.child_of(self).live().order_by('-first_published_at')
        return context

    class Meta:
        verbose_name = "Index des morceaux"
        verbose_name_plural = "Index des morceaux"


class Piece(Page):
    template = 'music/piece_detail.html'

    compositeur = models.CharField(max_length=250)
    descr = RichTextField(blank=True)
    traduction = RichTextField(blank=True)
    interpretation = RichTextField(blank=True)

    activer_timecodes = models.BooleanField(
        default=False,
        verbose_name="Activer les timecodes",
        help_text="Cochez pour activer la fonctionnalité de timecodes"
    )

    timecodes = StreamField([
        ('timecode', TimecodeBlock()),
    ], null=True, blank=True, use_json_field=True, verbose_name="Timecodes avec annotations")

    pdf = models.ForeignKey(
        Document,
        null=True, blank=True,
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
        FieldPanel('compositeur'),
        FieldPanel('descr'),
        FieldPanel('pdf'),
        FieldPanel('audios'),
        FieldPanel('additional_files'),
    ]

    advanced_panels = [
        FieldPanel('traduction'),
    ]

    interpretation_panels = [
        FieldPanel('interpretation'),
        FieldPanel('activer_timecodes'),
        FieldPanel('timecodes'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(base_panels, heading='Infos de base'),
        ObjectList(advanced_panels, heading='Traduction'),
        ObjectList(interpretation_panels, heading='Indications musicales'),
        ObjectList(Page.promote_panels, heading='Paramètres'),
    ])

    parent_page_types = ['music.PieceIndexPage']
    subpage_types = []

    def get_context(self, request):
        context = super().get_context(request)
        context['piece'] = self
        return context

    def get_sorted_timecodes(self):
        if not self.activer_timecodes:
            return []
        items = []
        for block in self.timecodes:
            if block.block_type == 'timecode':
                parts = block.value['timecode'].split(':')
                seconds = int(parts[0]) * 60 + int(parts[1])
                items.append((seconds, block))
        items.sort(key=lambda x: x[0])
        return [item[1] for item in items]

    def __str__(self):
        return f"{self.title} — {self.compositeur}"

    class Meta:
        verbose_name = "Morceau"
        verbose_name_plural = "Morceaux"


class RepertoireItemTag(TaggedItemBase):
    content_object = ParentalKey(
        'RepertoireItem',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )


class RepertoireItem(Orderable, ClusterableModel):
    repertoire = ParentalKey(
        'RepertoirePage',
        on_delete=models.CASCADE,
        related_name='items'
    )
    piece = models.ForeignKey(
        Piece,
        on_delete=models.CASCADE,
        related_name='repertoire_items',
        verbose_name="Morceau"
    )
    comment = models.TextField(blank=True, verbose_name="Commentaire")
    tags = ClusterTaggableManager(through=RepertoireItemTag, blank=True, verbose_name="Tags")

    panels = [
        FieldPanel('piece'),
        FieldPanel('comment'),
        FieldPanel('tags'),
    ]

    def __str__(self):
        return str(self.piece)


class RepertoirePage(Page):
    introduction = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        InlinePanel('items', label="Morceaux"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        tag = request.GET.get('tag')
        items = self.items.select_related('piece').prefetch_related('tags')
        if tag:
            items = items.filter(tags__name=tag)
        context['items'] = items.all()
        context['active_tag'] = tag
        return context

    class Meta:
        verbose_name = "Répertoire"
        verbose_name_plural = "Répertoires"
