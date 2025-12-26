from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='youtube_nocookie')
def youtube_nocookie(value):
    """
    Convertit les URLs YouTube en version no-cookie pour protéger la vie privée.
    Compatible avec les embeds Wagtail.
    """
    if not value:
        return value
    
    result = str(value)
    
    # Pattern 1: Remplacer dans les attributs src des iframes
    result = re.sub(
        r'(src=")https?://(?:www\.)?youtube\.com/embed/([^"?]+)([^"]*)"',
        r'\1https://www.youtube-nocookie.com/embed/\2?rel=0&modestbranding=1&controls=1&fs=1&enablejsapi=0"',
        result
    )
    
    # Pattern 2: Gérer les cas sans guillemets (moins probable mais possible)
    result = re.sub(
        r"(src=')https?://(?:www\.)?youtube\.com/embed/([^'?]+)([^']*)'",
        r"\1https://www.youtube-nocookie.com/embed/\2?rel=0&modestbranding=1&controls=1&fs=1&enablejsapi=0'",
        result
    )
    
    return mark_safe(result)
