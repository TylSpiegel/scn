from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from taggit.models import Tag

from apps.music.models.piece import TIMECODE_RE

register = template.Library()


@register.simple_tag
def repertoire_tags(page):
    """All tags used on items within a specific RepertoirePage."""
    from apps.music.models.piece import RepertoireItem
    ids = RepertoireItem.objects.filter(repertoire=page).values_list(
        'tagged_items__tag_id', flat=True
    ).distinct()
    return Tag.objects.filter(id__in=ids).order_by('name')


@register.filter(name='render_timecoded', is_safe=True)
def render_timecoded(text):
    """Convertit `[mm:ss]` en boutons Alpine `handleTimecode(...)`.

    Le reste du texte est échappé HTML. Les retours à la ligne deviennent <br>.
    Doit être rendu à l'intérieur du scope Alpine `pieceAudioPlayer()`.
    """
    if not text:
        return ''
    parts = []
    last = 0
    for m in TIMECODE_RE.finditer(text):
        parts.append(escape(text[last:m.start()]))
        tc = m.group(1)
        parts.append(
            '<button type="button" '
            'class="button is-small mx-1 timecode-btn" '
            f':class="lastTimecode === \'{tc}\' ? \'is-warning\' : \'is-primary\'" '
            f'@click="handleTimecode(\'{tc}\')">{tc}</button>'
        )
        last = m.end()
    parts.append(escape(text[last:]))
    return mark_safe(''.join(parts).replace('\n', '<br>'))
