from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods
from wagtail.models import Site

from apps.core.middleware import SESSION_KEY
from apps.core.models import SecuritySettings


def _safe_next(request, fallback: str = "/") -> str:
    next_url = request.GET.get("next") or request.POST.get("next") or fallback
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return fallback


@require_http_methods(["GET", "POST"])
def site_login(request):
    site = Site.find_for_request(request)
    settings_obj = SecuritySettings.for_site(site) if site else None
    expected = (settings_obj.password if settings_obj else "") or ""

    if not expected or request.user.is_authenticated or request.session.get(SESSION_KEY):
        return redirect(_safe_next(request))

    error = False
    if request.method == "POST":
        if request.POST.get("password", "") == expected:
            request.session.cycle_key()
            request.session[SESSION_KEY] = True
            return redirect(_safe_next(request))
        error = True

    return render(
        request,
        "password_required.html",
        {
            "settings_obj": settings_obj,
            "error": error,
            "next": _safe_next(request),
        },
    )


def check_password(request):
    if request.user.is_authenticated or request.session.get(SESSION_KEY):
        return HttpResponse(status=204)
    return HttpResponse(status=401)
