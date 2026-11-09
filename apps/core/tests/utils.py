"""Fixtures communes : une instance à deux faces (site public et site privé)."""

from types import SimpleNamespace

from django.test import override_settings
from wagtail.models import BaseViewRestriction, Page, PageViewRestriction, Site

from apps.content.models import ContentPage, HomePage
from apps.core.models import SecuritySettings
from apps.interaction.models import FormField, FormPage

PUBLIC_HOST = "public.test"
PRIVATE_HOST = "prive.test"
PASSWORD = "secret-membres"

two_hosts = override_settings(ALLOWED_HOSTS=[PUBLIC_HOST, PRIVATE_HOST])


def section(title, *content):
    return {
        "type": "section",
        "value": {"title": title, "date": "2026-01-01", "content": list(content)},
    }


def text(html):
    return {"type": "text", "value": html}


def build_sites():
    root = Page.get_first_root_node()
    Site.objects.all().delete()

    private_home = root.add_child(
        instance=HomePage(
            title="Accueil privé",
            slug="prive",
            name="Chorale",
            header="Bienvenue",
            body="<p>Accueil</p>",
        )
    )
    public_home = root.add_child(
        instance=ContentPage(
            title="Accueil public",
            slug="public",
            body=[section("Bienvenue", text("<p>Bonjour visiteur</p>"))],
        )
    )
    private_site = Site.objects.create(
        hostname=PRIVATE_HOST,
        port=80,
        root_page=private_home,
        is_default_site=True,
        site_name="Privé",
    )
    public_site = Site.objects.create(
        hostname=PUBLIC_HOST, port=80, root_page=public_home, site_name="Public"
    )
    SecuritySettings.objects.create(site=public_site, allow_indexing=True)

    restriction = PageViewRestriction.objects.create(
        page=private_home,
        restriction_type=BaseViewRestriction.PASSWORD,
        password=PASSWORD,
    )
    private_page = private_home.add_child(
        instance=ContentPage(
            title="Infos membres",
            slug="infos",
            body=[section("Secret", text("<p>Contenu réservé</p>"))],
        )
    )

    return SimpleNamespace(
        private_home=private_home,
        public_home=public_home,
        private_page=private_page,
        private_site=private_site,
        public_site=public_site,
        restriction=restriction,
    )


def add_form_page(parent, title="Contact", slug="contact"):
    page = FormPage(title=title, slug=slug, thank_you_text="<p>Merci beaucoup</p>")
    page.form_fields = [
        FormField(sort_order=0, label="Nom", field_type="singleline", required=True),
        FormField(sort_order=1, label="Message", field_type="multiline", required=True),
    ]
    return parent.add_child(instance=page)
