from .models import HomePage
from wagtail.models import Page


def first_level_page(request):
    menu_pages = Page.objects.live().in_menu()
    return {'menu_pages': menu_pages}
