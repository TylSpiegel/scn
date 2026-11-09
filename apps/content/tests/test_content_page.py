from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from wagtail.test.utils.form_data import nested_form_data, rich_text, streamfield

from apps.community.models import Event
from apps.content.models import ContentPage
from apps.core.tests.utils import (
    PRIVATE_HOST,
    PUBLIC_HOST,
    add_form_page,
    build_sites,
    section,
    text,
    two_hosts,
)
from apps.music.models import Piece, PieceIndexPage


@two_hosts
class ContentPageGuardTests(TestCase):
    """Événements, morceaux et formulaires privés sont refusés sur une page publique."""

    def setUp(self):
        self.sites = build_sites()
        self.client.force_login(
            User.objects.create_superuser("admin", "a@example.com", "x")
        )
        index = self.sites.private_home.add_child(
            instance=PieceIndexPage(title="Morceaux", slug="morceaux")
        )
        self.piece = index.add_child(
            instance=Piece(title="Ave Verum", slug="ave", compositeur="Mozart")
        )
        self.event = Event.objects.create(name="Concert", start_date=date(2026, 5, 1))
        self.private_form = add_form_page(
            self.sites.private_home, title="Inscription", slug="inscription"
        )
        self.public_form = add_form_page(self.sites.public_home)

    def _create(self, parent, *content):
        data = nested_form_data(
            {
                "title": "Nouvelle page",
                "slug": "nouvelle",
                "template_variant": "standard",
                "body": streamfield(
                    [
                        (
                            "section",
                            {
                                "title": "Section",
                                "date": "",
                                "content": streamfield(list(content)),
                            },
                        ),
                    ]
                ),
            }
        )
        url = reverse(
            "wagtailadmin_pages:add", args=("content", "contentpage", parent.pk)
        )
        return self.client.post(url, data, HTTP_HOST=PRIVATE_HOST)

    def _created(self):
        return ContentPage.objects.filter(slug="nouvelle").exists()

    def test_piece_refused_on_public_page(self):
        response = self._create(self.sites.public_home, ("piece", self.piece.pk))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cette page est publique")
        self.assertFalse(self._created())

    def test_event_refused_on_public_page(self):
        self._create(
            self.sites.public_home,
            ("event", {"event": self.event.pk, "extra_content": rich_text("")}),
        )
        self.assertFalse(self._created())

    def test_private_form_refused_on_public_page(self):
        self._create(self.sites.public_home, ("form", self.private_form.pk))
        self.assertFalse(self._created())

    def test_public_form_allowed_on_public_page(self):
        self._create(
            self.sites.public_home,
            ("form", self.public_form.pk),
            ("text", rich_text("<p>Salut</p>")),
        )
        self.assertTrue(self._created())

    def test_private_blocks_allowed_on_private_page(self):
        self._create(
            self.sites.private_home,
            ("piece", self.piece.pk),
            ("event", {"event": self.event.pk, "extra_content": rich_text("")}),
            ("form", self.private_form.pk),
        )
        self.assertTrue(self._created())


@two_hosts
class ContentPageTemplateTests(TestCase):
    def setUp(self):
        self.sites = build_sites()

    def test_each_variant_uses_its_template(self):
        page = self.sites.public_home
        for variant, _ in ContentPage.TEMPLATE_CHOICES:
            page.template_variant = variant
            page.save()
            response = self.client.get("/", HTTP_HOST=PUBLIC_HOST)
            self.assertTemplateUsed(response, f"content/content_page_{variant}.html")
            self.assertContains(response, "Bonjour visiteur")

    def test_sections_render_title_and_content(self):
        page = self.sites.public_home
        page.body = [
            section("Première", text("<p>Un</p>")),
            section("Seconde", text("<p>Deux</p>")),
        ]
        page.save()
        response = self.client.get("/", HTTP_HOST=PUBLIC_HOST)
        content = response.content.decode()
        self.assertLess(content.index("Première"), content.index("Seconde"))
        self.assertContains(response, "<p>Deux</p>", html=True)

    def test_section_without_title(self):
        page = self.sites.public_home
        page.body = [
            {
                "type": "section",
                "value": {
                    "title": "",
                    "date": None,
                    "content": [text("<p>Sans titre</p>")],
                },
            }
        ]
        page.save()
        response = self.client.get("/", HTTP_HOST=PUBLIC_HOST)
        self.assertContains(response, "Sans titre")
        self.assertContains(response, "has-no-heading")
        self.assertNotContains(response, '<h2 class="title is-4"></h2>', html=True)
