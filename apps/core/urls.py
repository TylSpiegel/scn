from django.urls import path

from apps.core import views


urlpatterns = [
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
]
