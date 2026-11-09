from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Palette, ThemeSettings
from apps.core.models.theme import PALETTE_SLOTS, contrast_ratio
from apps.core.tests.utils import PRIVATE_HOST, PUBLIC_HOST, build_sites, two_hosts


class ContrastTests(TestCase):
    def test_contrast_ratio(self):
        self.assertAlmostEqual(contrast_ratio("#000000", "#ffffff"), 21, places=1)
        self.assertAlmostEqual(contrast_ratio("#777777", "#777777"), 1)

    def test_defaults_are_valid(self):
        Palette(slot=1, name="Défaut").clean()

    def test_presets_are_valid(self):
        for palette in Palette.objects.all():
            palette.clean()

    def test_unreadable_text_is_refused(self):
        palette = Palette(text_color="#eeeeee", background_color="#f5f5f5")
        with self.assertRaises(ValidationError) as ctx:
            palette.clean()
        self.assertIn("text_color", ctx.exception.message_dict)

    def test_too_light_primary_is_refused(self):
        with self.assertRaises(ValidationError) as ctx:
            Palette(primary_color="#ffe4ec").clean()
        self.assertIn("primary_color", ctx.exception.message_dict)

    def test_custom_navbar_checked_only_when_not_following_primary(self):
        Palette(navbar_bg="#ffffff", navbar_text="#ffffff").clean()
        with self.assertRaises(ValidationError):
            Palette(
                navbar_follows_primary=False, navbar_bg="#ffffff", navbar_text="#ffffff"
            ).clean()


class PaletteSlotsTests(TestCase):
    def test_five_palettes_after_migration(self):
        self.assertEqual(Palette.objects.count(), PALETTE_SLOTS)
        self.assertEqual(
            list(Palette.objects.values_list("slot", flat=True)), [1, 2, 3, 4, 5]
        )

    def test_admin_can_edit_but_not_add_or_delete(self):
        self.client.force_login(
            User.objects.create_superuser("admin", "a@example.com", "x")
        )
        palette = Palette.objects.first()

        self.assertEqual(
            self.client.get(reverse("wagtailsnippets_core_palette:list")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse("wagtailsnippets_core_palette:edit", args=[palette.pk])
            ).status_code,
            200,
        )
        self.assertNotEqual(
            self.client.get(reverse("wagtailsnippets_core_palette:add")).status_code,
            200,
        )
        self.client.post(
            reverse("wagtailsnippets_core_palette:delete", args=[palette.pk])
        )
        self.assertTrue(Palette.objects.filter(pk=palette.pk).exists())


@two_hosts
class ThemeRenderingTests(TestCase):
    def setUp(self):
        self.sites = build_sites()

    def test_site_uses_its_palette(self):
        palette = Palette.objects.get(slot=2)
        palette.primary_color = "#123456"
        palette.save()
        ThemeSettings.objects.create(site=self.sites.public_site, palette=palette)

        response = self.client.get("/", HTTP_HOST=PUBLIC_HOST)
        self.assertContains(response, "--primary-color: #123456;")
        self.assertContains(response, "--navbar-bg: #123456;")
        self.assertContains(response, "--event-concert-color: var(--secondary-color);")

        # L'autre site n'a pas choisi de palette : il prend la première
        response = self.client.get("/robots.txt", HTTP_HOST=PRIVATE_HOST)
        self.assertNotContains(response, "#123456")

    def test_custom_navbar(self):
        palette = Palette.objects.get(slot=1)
        palette.navbar_follows_primary = False
        palette.navbar_bg = "#000000"
        palette.save()
        ThemeSettings.objects.create(site=self.sites.public_site, palette=palette)
        response = self.client.get("/", HTTP_HOST=PUBLIC_HOST)
        self.assertContains(response, "--navbar-bg: #000000;")

    def test_default_palette_without_theme_settings(self):
        response = self.client.get("/", HTTP_HOST=PUBLIC_HOST)
        self.assertContains(
            response, f"--primary-color: {Palette.objects.get(slot=1).primary_color};"
        )
