import re

from django.db import models

from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel, TabbedInterface, ObjectList
from wagtail.documents.models import Document
from wagtail.fields import RichTextField, StreamField
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase

from apps.music.blocks import AudioDocumentBlock, AdditionalFilesBlock


TIMECODE_RE = re.compile(r'\[(\d{1,2}:\d{2})\]')


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

    timecodes = models.TextField(
        blank=True,
        verbose_name="Paroles avec timecodes",
        help_text=(
            "Texte libre. Insérez des timecodes au format [mm:ss] dans les paroles ; "
            "ils seront convertis en boutons cliquables dans le lecteur. "
            "Exemple : [00:10]Ave Maria, gratia plena\\nDominus tecum, [00:20]Ave Maria"
        ),
    )

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

    def get_parsed_timecodes(self):
        """Liste triée et dédoublonnée des timecodes mm:ss trouvés dans le texte."""
        if not self.activer_timecodes or not self.timecodes:
            return []
        seen = set()
        out = []
        for m in TIMECODE_RE.finditer(self.timecodes):
            tc = m.group(1)
            if tc in seen:
                continue
            seen.add(tc)
            out.append(tc)

        def _key(s):
            mm, ss = s.split(':')
            return int(mm) * 60 + int(ss)

        return sorted(out, key=_key)

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
        if self.piece_id:
            return str(self.piece)
        return "(nouveau morceau)"


class RepertoirePage(Page):
    introduction = models.TextField(blank=True)
    ordre_important = models.BooleanField(
        default=False,
        verbose_name="Ordre important",
        help_text="Si coché, les morceaux sont numérotés (#1, #2, …) dans l'ordre du répertoire."
    )

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('ordre_important'),
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
