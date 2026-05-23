from django import template
from taggit.models import Tag

register = template.Library()


@register.simple_tag
def repertoire_tags(page):
    """All tags used on items within a specific RepertoirePage."""
    from apps.music.models.piece import RepertoireItem
    ids = RepertoireItem.objects.filter(repertoire=page).values_list(
        'taggit_taggeditem_items__tag_id', flat=True
    ).distinct()
    return Tag.objects.filter(id__in=ids).order_by('name')


@register.simple_tag
def community_tags():
    """All tags used on Events."""
    from apps.community.models.event import EventTag
    ids = EventTag.objects.values_list('tag_id', flat=True).distinct()
    return Tag.objects.filter(id__in=ids).order_by('name')
