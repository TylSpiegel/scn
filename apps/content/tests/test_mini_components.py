import tempfile
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from PIL import Image as PILImage
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail.models import Collection, CollectionViewRestriction

from apps.content.blocks import ButtonBlock
from apps.content.models import private_content_in
from apps.core.tests.utils import PUBLIC_HOST, build_sites, section, two_hosts

TABLE = {
    "data": [["Pupitre", "Places"], ["Basses", "Complet"], ["Ténors", "Libres"]],
    "first_row_is_table_header": True,
    "first_col_is_header": False,
    "table_caption": "Places par pupitre",
}


def _png():
    buffer = BytesIO()
    PILImage.new("RGB", (10, 10), "purple").save(buffer, "PNG")
    return ContentFile(buffer.getvalue(), name="photo.png")


@two_hosts
class MiniComponentsRenderingTests(TestCase):
    def setUp(self):
        self.sites = build_sites()
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        media_override = override_settings(MEDIA_ROOT=self.media.name)
        media_override.enable()
        self.addCleanup(media_override.disable)

    def test_all_components_render(self):
        image = Image.objects.create(title="Concert", file=_png())
        document = Document.objects.create(
            title="Programme",
            collection=Collection.objects.get(name="Public"),
            file=ContentFile(b"%PDF", name="programme.pdf"),
        )
        page = self.sites.public_home
        page.body = [
            section(
                "Tout",
                {"type": "button", "value": {"label": "Réserver", "page": page.pk, "url": "", "style": "filled"}},
                {"type": "callout", "value": {"text": "<p>Répétition déplacée</p>", "tone": "important"}},
                {"type": "quote", "value": {"text": "Chanter, c'est prier deux fois", "author": "Saint Augustin"}},
                {"type": "image", "value": {"image": image.pk, "caption": "Juin 2025"}},
                {"type": "practical_info", "value": {"kind": "place", "text": "Église Saint-Nicolas"}},
                {"type": "key_figure", "value": {"number": "40", "label": "choristes"}},
                {"type": "table", "value": TABLE},
                {"type": "document", "value": document.pk},
                {"type": "separator", "value": None},
                {"type": "spacer", "value": "large"},
            )
        ]
        page.save()

        response = self.client.get("/", HTTP_HOST=PUBLIC_HOST)
        for expected in (
            'class="button is-primary is-rounded"',
            "block-callout is-important",
            "Saint Augustin",
            "Juin 2025",
            "fa-location-dot",
            "Lieu : ",
            "choristes",
            "Places par pupitre",
            "<th",
            "Programme",
            "block-separator",
            "block-spacer is-large",
        ):
            self.assertContains(response, expected)


class ButtonBlockTests(TestCase):
    def test_needs_page_or_url(self):
        block = ButtonBlock()
        with self.assertRaises(ValidationError):
            block.clean(block.to_python({"label": "Go", "page": None, "url": "", "style": "filled"}))

    def test_external_url(self):
        block = ButtonBlock()
        value = block.clean(block.to_python({"label": "Go", "page": None, "url": "https://example.com", "style": "outlined"}))
        self.assertEqual(value["url"], "https://example.com")


class DocumentGuardTests(TestCase):
    def setUp(self):
        self.sites = build_sites()
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)

    def _page_with(self, collection_name):
        with override_settings(MEDIA_ROOT=self.media.name):
            document = Document.objects.create(
                title="PV",
                collection=Collection.objects.get(name=collection_name),
                file=ContentFile(b"x", name="pv.txt"),
            )
        page = self.sites.public_home
        page.body = [section("Docs", {"type": "document", "value": document.pk})]
        page.save()
        return page

    def test_members_document_is_private_content(self):
        members = Collection.objects.get(name="Espace membres")
        CollectionViewRestriction.objects.get_or_create(
            collection=members, restriction_type="password", defaults={"password": "x"}
        )
        page = self._page_with("Espace membres")
        self.assertEqual(len(private_content_in(page.body)), 1)

    def test_public_document_is_allowed(self):
        page = self._page_with("Public")
        self.assertEqual(private_content_in(page.body), [])
