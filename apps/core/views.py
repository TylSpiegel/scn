from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET
from wagtail.contrib.sitemaps.views import sitemap as wagtail_sitemap

from apps.core.models import SecuritySettings


# Robots d'entraînement et d'assistants IA, bloqués même quand l'indexation est autorisée.
AI_CRAWLERS = (
    "GPTBot",
    "ChatGPT-User",
    "OAI-SearchBot",
    "ClaudeBot",
    "Claude-Web",
    "anthropic-ai",
    "CCBot",
    "Google-Extended",
    "Applebot-Extended",
    "PerplexityBot",
    "Bytespider",
    "Amazonbot",
    "Meta-ExternalAgent",
    "FacebookBot",
    "cohere-ai",
    "Diffbot",
    "ImagesiftBot",
    "Omgilibot",
)


def _allow_indexing(request) -> bool:
    return SecuritySettings.for_request(request).allow_indexing


@require_GET
def robots_txt(request):
    if not _allow_indexing(request):
        lines = ["User-agent: *", "Disallow: /"]
    else:
        lines = [f"User-agent: {bot}" for bot in AI_CRAWLERS]
        lines += [
            "Disallow: /",
            "",
            "User-agent: *",
            "Disallow: /admin/",
            "Disallow: /django-admin/",
            "Disallow: /documents/",
            "",
            f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


@require_GET
def sitemap(request):
    if not _allow_indexing(request):
        raise Http404
    return wagtail_sitemap(request)
