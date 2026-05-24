from django import template
from taggit.models import Tag

register = template.Library()


@register.simple_tag
def repertoire_tags(page):
    """All tags used on items within a specific RepertoirePage."""
    from apps.music.models.piece import RepertoireItem
    ids = RepertoireItem.objects.filter(repertoire=page).values_list(
        'tagged_items__tag_id', flat=True
    ).distinct()
    return Tag.objects.filter(id__in=ids).order_by('name')
