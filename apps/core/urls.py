"""URL Configuration for website project."""
from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images import urls as wagtailimages_urls

from search import views as search_views

urlpatterns = [
    # Django Admin
    path("django-admin/", admin.site.urls),

    # Wagtail Admin
    path("admin/", include(wagtailadmin_urls)),

    # Wagtail documents and images
    path("documents/", include(wagtaildocs_urls)),
    path("images/", include(wagtailimages_urls)),

    # Custom app URLs
    path("music/", include("apps.music.urls")),
    path("community/", include("apps.community.urls")),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's serving mechanism
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Django Debug Toolbar
    try:
        import debug_toolbar

        urlpatterns = [
                          path('__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns
    except ImportError:
        pass
