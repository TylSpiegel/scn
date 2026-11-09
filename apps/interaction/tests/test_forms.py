from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from wagtail.contrib.forms.models import FormSubmission

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
from apps.interaction.models.forms import HONEYPOT_FIELD, ORIGIN_FIELD


@two_hosts
class FormPageTests(TestCase):
    def setUp(self):
        self.sites = build_sites()
        self.form_page = add_form_page(self.sites.public_home)
        self.page = self.sites.public_home.add_child(
            instance=ContentPage(
                title="Nous rejoindre",
                slug="rejoindre",
                body=[
                    section(
                        "Contact",
                        text("<p>Écrivez-nous</p>"),
                        {"type": "form", "value": self.form_page.pk},
                    )
                ],
            )
        )

    def _post(self, url, host=PUBLIC_HOST, **data):
        payload = {"nom": "Claire", "message": "Bonjour"}
        payload.update(data)
        return self.client.post(url, payload, HTTP_HOST=host)

    def test_form_block_renders_the_form(self):
        response = self.client.get("/rejoindre/", HTTP_HOST=PUBLIC_HOST)
        self.assertContains(response, 'action="/contact/"')
        self.assertContains(response, f'name="{ORIGIN_FIELD}" value="{self.page.pk}"')
        self.assertContains(response, f'name="{HONEYPOT_FIELD}"')

    def test_submission_from_content_page_returns_to_origin(self):
        response = self._post("/contact/", **{ORIGIN_FIELD: self.page.pk})
        self.assertRedirects(
            response,
            f"/rejoindre/#form-{self.form_page.pk}",
            fetch_redirect_response=False,
        )

        submission = FormSubmission.objects.get(page=self.form_page)
        self.assertEqual(submission.get_data()["nom"], "Claire")
        self.assertNotIn(HONEYPOT_FIELD, submission.form_data)
        self.assertNotIn(ORIGIN_FIELD, submission.form_data)

        response = self.client.get("/rejoindre/", HTTP_HOST=PUBLIC_HOST)
        self.assertContains(response, "Merci beaucoup")

    def test_direct_submission_shows_landing_page(self):
        response = self._post("/contact/")
        self.assertTemplateUsed(response, "interaction/form_page_landing.html")
        self.assertEqual(FormSubmission.objects.count(), 1)

    def test_honeypot_discards_submission(self):
        response = self._post("/contact/", **{HONEYPOT_FIELD: "http://spam.example"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FormSubmission.objects.count(), 0)

    def test_private_form_requires_password(self):
        add_form_page(self.sites.private_home, title="Inscription", slug="inscription")
        response = self._post("/inscription/", host=PRIVATE_HOST)
        self.assertTemplateUsed(response, "password_required.html")
        self.assertEqual(FormSubmission.objects.count(), 0)

    def test_xlsx_export(self):
        self._post("/contact/")
        self.client.force_login(
            User.objects.create_superuser("admin", "a@example.com", "x")
        )
        url = reverse("wagtailforms:list_submissions", args=(self.form_page.pk,))
        response = self.client.get(url, {"export": "xlsx"}, HTTP_HOST=PRIVATE_HOST)
        self.assertEqual(response.status_code, 200)
        self.assertIn("spreadsheetml", response["Content-Type"])
