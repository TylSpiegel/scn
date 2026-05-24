"""
Initialise la structure de pages minimale pour une nouvelle instance.

Usage :
    python manage.py setup_site
    python manage.py setup_site --site-name "Ma Chorale" --hostname example.com --port 80

Idempotent : peut être relancé sans risque si les pages existent déjà.
"""
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from apps.content.models import HomePage
from apps.community.models.pages import CalendrierPage, ChoristesIndexPage
from apps.music.models import PieceIndexPage
from apps.core.models.navigation import NavigationSettings, MenuItem


class Command(BaseCommand):
    help = "Crée les pages structurelles minimales et configure la navigation."

    def add_arguments(self, parser):
        parser.add_argument('--site-name', default='Chorale SCN', help='Nom du site Wagtail')
        parser.add_argument('--hostname', default='localhost', help='Hostname du site')
        parser.add_argument('--port', type=int, default=8000, help='Port du site')

    def handle(self, *args, **options):
        home = self._ensure_homepage()
        site = self._ensure_site(home, options)

        calendrier = self._ensure_page(
            CalendrierPage, parent=home,
            title="Calendrier", slug="calendrier",
            show_in_menus=True, show_calendar=True, how_many_events=5,
        )
        choristes = self._ensure_page(
            ChoristesIndexPage, parent=home,
            title="Choristes", slug="choristes",
            show_in_menus=True,
        )
        morceaux = self._ensure_page(
            PieceIndexPage, parent=home,
            title="Morceaux", slug="morceaux",
            show_in_menus=True,
        )

        self._ensure_nav(site, [
            ("Calendrier", calendrier),
            ("Choristes",  choristes),
            ("Morceaux",   morceaux),
        ])

        self.stdout.write(self.style.SUCCESS("Setup terminé."))

    # ------------------------------------------------------------------ #

    def _ensure_homepage(self):
        home = HomePage.objects.first()
        if home:
            self.stdout.write(f"  [ok] HomePage existante : « {home.title} »")
            return home

        root = Page.objects.filter(depth=1).first()
        if root is None:
            self.stderr.write("Aucune page racine trouvée. Lancez d'abord `migrate`.")
            raise SystemExit(1)

        home = HomePage(
            title="Accueil", slug="accueil",
            name="Société Chorale", header="Bienvenue",
            body="<p>Bienvenue sur le site de la chorale.</p>",
            show_in_menus=False,
        )
        root.add_child(instance=home)
        self.stdout.write(self.style.SUCCESS("  [créé] HomePage « Accueil »"))
        return home

    def _ensure_site(self, home, options):
        site = Site.objects.filter(is_default_site=True).first()
        if site:
            if site.root_page_id != home.pk:
                site.root_page = home
                site.save()
                self.stdout.write("  [mis à jour] Site → HomePage")
            else:
                self.stdout.write("  [ok] Site Wagtail déjà configuré")
            return site

        site = Site.objects.create(
            hostname=options['hostname'],
            port=options['port'],
            site_name=options['site_name'],
            root_page=home,
            is_default_site=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f"  [créé] Site « {options['site_name']} » sur {options['hostname']}:{options['port']}"
        ))
        return site

    def _ensure_page(self, model, parent, title, slug, **fields):
        existing = model.objects.first()
        if existing:
            self.stdout.write(f"  [ok] {model.__name__} existante")
            return existing
        page = model(title=title, slug=slug, **fields)
        parent.add_child(instance=page)
        self.stdout.write(self.style.SUCCESS(f"  [créé] {model.__name__} « {title} »"))
        return page

    def _ensure_nav(self, site, entries):
        """Ajoute les entrées de menu manquantes dans NavigationSettings."""
        nav = NavigationSettings.for_site(site)
        if not nav.pk:
            nav.site_name = site.site_name
            nav.save()
            self.stdout.write(self.style.SUCCESS("  [créé] NavigationSettings"))
        else:
            self.stdout.write("  [ok] NavigationSettings existant")

        existing_pages = set(
            nav.menu_items.filter(link_page__isnull=False)
                          .values_list('link_page_id', flat=True)
        )

        for order, (title, page) in enumerate(entries):
            if page.pk in existing_pages:
                self.stdout.write(f"  [ok] Lien nav « {title} » déjà présent")
                continue
            MenuItem.objects.create(
                navigation=nav,
                title=title,
                link_page=page,
                show_on_mobile=True,
                sort_order=order,
            )
            self.stdout.write(self.style.SUCCESS(f"  [créé] Lien nav « {title} »"))
