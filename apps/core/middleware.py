from django.shortcuts import redirect
from django.urls import reverse
from wagtail.models import Site

from apps.core.models import SecuritySettings


SESSION_KEY = "site_auth_ok"

EXEMPT_PREFIXES = (
    "/admin/",
    "/django-admin/",
    "/_site_login/",
    "/_check_password/",
    "/static/",
    "/media/",
    "/favicon.ico",
)


def _is_exempt_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in EXEMPT_PREFIXES)


def _get_password(request) -> str:
    site = Site.find_for_request(request)
    if site is None:
        return ""
    return SecuritySettings.for_site(site).password or ""


class SitePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if _is_exempt_path(request.path):
            return self.get_response(request)

        if request.user.is_authenticated:
            return self.get_response(request)

        if request.session.get(SESSION_KEY):
            return self.get_response(request)

        if not _get_password(request):
            return self.get_response(request)

        login_url = reverse("site_login")
        return redirect(f"{login_url}?next={request.get_full_path()}")
