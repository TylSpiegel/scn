import tempfile
from io import StringIO

from django.contrib.auth.models import Group, User
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from wagtail.documents.models import Document
from wagtail.models import Collection, CollectionViewRestriction

from apps.core.tests.utils import (
    PASSWORD,
    PRIVATE_HOST,
    PUBLIC_HOST,
    build_sites,
    two_hosts,
)


@two_hosts
class PagePrivacyTests(TestCase):
    def setUp(self):
        self.sites = build_sites()

    def test_private_page_asks_for_password(self):
        response = self.client.get("/infos/", HTTP_HOST=PRIVATE_HOST)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_required.html")
        self.assertNotContains(response, "Contenu réservé")

    def test_private_page_after_password(self):
        response = self.client.get("/infos/", HTTP_HOST=PRIVATE_HOST)
        self.client.post(
            response.context["action_url"],
            {
                "password": PASSWORD,
                "return_url": "/infos/",
            },
            HTTP_HOST=PRIVATE_HOST,
        )
        response = self.client.get("/infos/", HTTP_HOST=PRIVATE_HOST)
        self.assertContains(response, "Contenu réservé")

    def test_wrong_password_is_refused(self):
        response = self.client.get("/infos/", HTTP_HOST=PRIVATE_HOST)
        response = self.client.post(
            response.context["action_url"],
            {
                "password": "mauvais",
                "return_url": "/infos/",
            },
            HTTP_HOST=PRIVATE_HOST,
        )
        self.assertContains(response, "Le mot de passe est incorrect.")

    def test_private_page_not_reachable_from_public_host(self):
        response = self.client.get("/infos/", HTTP_HOST=PUBLIC_HOST)
        self.assertEqual(response.status_code, 404)

    def test_public_page_is_open(self):
        response = self.client.get("/", HTTP_HOST=PUBLIC_HOST)
        self.assertContains(response, "Bonjour visiteur")

    def test_admin_users_skip_the_password(self):
        user = User.objects.create_user("modo", password="x")
        user.groups.add(Group.objects.get(name="Modérateurs"))
        self.client.force_login(user)
        response = self.client.get("/infos/", HTTP_HOST=PRIVATE_HOST)
        self.assertContains(response, "Contenu réservé")


@two_hosts
class DocumentPrivacyTests(TestCase):
    def setUp(self):
        self.sites = build_sites()
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        media_override = override_settings(MEDIA_ROOT=self.media.name)
        media_override.enable()
        self.addCleanup(media_override.disable)

        members = Collection.objects.get(name="Espace membres")
        CollectionViewRestriction.objects.filter(collection=members).delete()
        CollectionViewRestriction.objects.create(
            collection=members, restriction_type="password", password=PASSWORD
        )
        self.private_doc = Document.objects.create(
            title="PV",
            collection=members,
            file=ContentFile(b"prive", name="pv.txt"),
        )
        self.public_doc = Document.objects.create(
            title="Affiche",
            collection=Collection.objects.get(name="Public"),
            file=ContentFile(b"public", name="affiche.txt"),
        )

    def test_members_document_asks_for_password_on_both_hosts(self):
        for host in (PUBLIC_HOST, PRIVATE_HOST):
            response = self.client.get(self.private_doc.url, HTTP_HOST=host)
            self.assertTemplateUsed(response, "password_required.html")

    def test_public_document_is_served(self):
        response = self.client.get(self.public_doc.url, HTTP_HOST=PUBLIC_HOST)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"public")

    def test_member_does_not_retype_password_for_documents(self):
        response = self.client.get("/infos/", HTTP_HOST=PRIVATE_HOST)
        self.client.post(
            response.context["action_url"],
            {
                "password": PASSWORD,
                "return_url": "/infos/",
            },
            HTTP_HOST=PRIVATE_HOST,
        )
        response = self.client.get(self.private_doc.url, HTTP_HOST=PRIVATE_HOST)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"prive")


class CheckPrivacyCommandTests(TestCase):
    def setUp(self):
        self.sites = build_sites()

    def test_ok_when_private_root_is_restricted(self):
        call_command("check_privacy", stdout=StringIO())

    def test_fails_when_private_root_is_open(self):
        self.sites.restriction.delete()
        with self.assertRaises(CommandError):
            call_command("check_privacy", stdout=StringIO())
