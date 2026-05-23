from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.snippets.models import register_snippet

from .models import Piece


class PieceViewSet(SnippetViewSet):
    model = Piece
    icon = 'media'
    menu_label = 'Morceaux'
    list_display = ['titre', 'compositeur']
    search_fields = ['titre', 'compositeur']
    ordering = ['titre']


class MusicGroup(SnippetViewSetGroup):
    items = [PieceViewSet]
    icon = 'media'
    menu_label = 'Musique'
    menu_name = 'music'
    menu_order = 400


register_snippet(MusicGroup)
