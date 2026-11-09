from django.test import TestCase

from apps.core.tests.utils import PRIVATE_HOST, PUBLIC_HOST, build_sites, two_hosts


@two_hosts
class IndexingTests(TestCase):
    def setUp(self):
        self.sites = build_sites()

    def test_public_site_is_indexable(self):
        response = self.client.get("/", HTTP_HOST=PUBLIC_HOST)
        self.assertContains(
            response, '<meta name="robots" content="index, follow">', html=True
        )
        self.assertContains(response, 'property="og:title"')

    def test_private_site_is_not_indexable(self):
        self.client.cookies.clear()
        response = self.client.get("/", HTTP_HOST=PRIVATE_HOST)
        self.assertContains(
            response, '<meta name="robots" content="noindex, nofollow">', html=True
        )

    def test_robots_txt_public_blocks_ai_crawlers(self):
        response = self.client.get("/robots.txt", HTTP_HOST=PUBLIC_HOST)
        body = response.content.decode()
        self.assertIn("User-agent: GPTBot", body)
        self.assertIn("User-agent: ClaudeBot", body)
        self.assertIn(f"Sitemap: http://{PUBLIC_HOST}/sitemap.xml", body)

    def test_robots_txt_private_blocks_everything(self):
        response = self.client.get("/robots.txt", HTTP_HOST=PRIVATE_HOST)
        self.assertEqual(response.content.decode(), "User-agent: *\nDisallow: /\n")

    def test_sitemap_lists_public_pages_only(self):
        response = self.client.get("/sitemap.xml", HTTP_HOST=PUBLIC_HOST)
        self.assertContains(response, f"http://{PUBLIC_HOST}/")
        self.assertNotContains(response, "/infos/")

    def test_sitemap_absent_on_private_site(self):
        response = self.client.get("/sitemap.xml", HTTP_HOST=PRIVATE_HOST)
        self.assertEqual(response.status_code, 404)
