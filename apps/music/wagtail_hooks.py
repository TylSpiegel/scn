from django.urls import path

from wagtail import hooks
from wagtail.admin.menu import MenuItem


@hooks.register('register_admin_urls')
def register_music_admin_urls():
    from . import admin_views
    return [
        path('morceaux/', admin_views.piece_explorer_redirect, name='music-morceaux'),
    ]


@hooks.register('register_admin_menu_item')
def register_music_menu_item():
    return MenuItem(
        'Musique',
        '/admin/morceaux/',
        icon_name='media',
        order=200,
        name='music',
    )
