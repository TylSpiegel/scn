from django.urls import path

from apps.core import views


urlpatterns = [
    path("_site_login/", views.site_login, name="site_login"),
    path("_check_password/", views.check_password, name="site_check_password"),
]
