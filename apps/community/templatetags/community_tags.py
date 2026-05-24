from django import template
from taggit.models import Tag

register = template.Library()


@register.simple_tag
def community_tags():
    """All tags used on Events."""
    from apps.community.models.event import EventTag
    ids = EventTag.objects.values_list('tag_id', flat=True).distinct()
    return Tag.objects.filter(id__in=ids).order_by('name')
