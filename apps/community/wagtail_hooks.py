from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.snippets.models import register_snippet

from .models import Event, Role, Choriste


class EventViewSet(SnippetViewSet):
    model = Event
    icon = 'date'
    menu_label = 'Événements'
    list_display = ['__str__', 'start_date', 'lieu']
    search_fields = ['name', 'lieu']
    ordering = ['-start_date']


class RoleViewSet(SnippetViewSet):
    model = Role
    icon = 'pick'
    menu_label = 'Fonctions'
    list_display = ['name']
    search_fields = ['name']


class ChoristeViewSet(SnippetViewSet):
    model = Choriste
    icon = 'user'
    menu_label = 'Choristes'
    list_display = ['name', 'pupitre', 'active']
    search_fields = ['name']


class CommunityGroup(SnippetViewSetGroup):
    items = [EventViewSet, RoleViewSet, ChoristeViewSet]
    icon = 'group'
    menu_label = 'Communauté'
    menu_name = 'community'
    menu_order = 150


register_snippet(CommunityGroup)
