"""
Initialise la structure de pages minimale pour une nouvelle instance.

Usage :
    python manage.py setup_site
    python manage.py setup_site --site-name "Ma Chorale" --hostname example.com --port 80
    python manage.py setup_site --hostname prive.example.com --port 443 \
        --public-hostname example.com --public-site-name "Ma Chorale" --members-password "..."

Le site privé (HomePage) est protégé par le mot de passe des membres (restriction native
de Wagtail). Avec --public-hostname, un second site public est créé, dont la racine est
une ContentPage ordinaire.

Idempotent : peut être relancé sans risque si les pages existent déjà.
"""

from django.core.management.base import BaseCommand
from wagtail.models import (
    BaseViewRestriction,
    Collection,
    CollectionViewRestriction,
    Page,
    PageViewRestriction,
    Site,
)

from apps.content.models import ContentPage, HomePage
from apps.community.models.pages import CalendrierPage, ChoristesIndexPage
from apps.music.models import PieceIndexPage
from apps.core.models.navigation import NavigationSettings, MenuItem
from apps.core.models.security import SecuritySettings


MEMBERS_COLLECTION = "Espace membres"
PUBLIC_COLLECTION = "Public"


class Command(BaseCommand):
    help = "Crée les pages structurelles minimales et configure la navigation."

    def add_arguments(self, parser):
        parser.add_argument(
            "--site-name", default="Chorale SCN", help="Nom du site Wagtail"
        )
        parser.add_argument("--hostname", default="localhost", help="Hostname du site")
        parser.add_argument("--port", type=int, default=8000, help="Port du site")
        parser.add_argument(
            "--members-password",
            default="",
            help="Mot de passe des membres (pages privées et documents « Espace membres »), "
            "posé seulement s'il n'y a pas encore de restriction",
        )
        parser.add_argument(
            "--public-hostname", default="", help="Hostname du site public (optionnel)"
        )
        parser.add_argument(
            "--public-port",
            type=int,
            default=None,
            help="Port du site public (défaut : --port)",
        )
        parser.add_argument(
            "--public-site-name",
            default="",
            help="Nom du site public (défaut : --site-name)",
        )

    def handle(self, *args, **options):
        home = self._ensure_homepage()
        site = self._ensure_site(home, options)

        calendrier = self._ensure_page(
            CalendrierPage,
            parent=home,
            title="Calendrier",
            slug="calendrier",
            show_in_menus=True,
            show_calendar=True,
            how_many_events=5,
        )
        choristes = self._ensure_page(
            ChoristesIndexPage,
            parent=home,
            title="Choristes",
            slug="choristes",
            show_in_menus=True,
        )
        morceaux = self._ensure_page(
            PieceIndexPage,
            parent=home,
            title="Morceaux",
            slug="morceaux",
            show_in_menus=True,
        )

        self._ensure_child(home, ContentPage, title="Formulaires", slug="formulaires")

        self._ensure_nav(
            site,
            [
                ("Calendrier", calendrier),
                ("Choristes", choristes),
                ("Morceaux", morceaux),
            ],
        )

        members = self._ensure_collections()
        self._ensure_members_restriction(home, members, options["members_password"])

        if options["public_hostname"]:
            self._ensure_public_site(options)

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
            title="Accueil",
            slug="accueil",
            name="Société Chorale",
            header="Bienvenue",
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
            hostname=options["hostname"],
            port=options["port"],
            site_name=options["site_name"],
            root_page=home,
            is_default_site=True,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"  [créé] Site « {options['site_name']} » sur {options['hostname']}:{options['port']}"
            )
        )
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

    def _ensure_child(self, parent, model, title, slug, **fields):
        existing = parent.get_children().filter(slug=slug).first()
        if existing:
            self.stdout.write(f"  [ok] {model.__name__} « {existing.title} » existante")
            return existing.specific
        page = model(title=title, slug=slug, **fields)
        parent.add_child(instance=page)
        self.stdout.write(self.style.SUCCESS(f"  [créé] {model.__name__} « {title} »"))
        return page

    def _ensure_collections(self):
        root = Collection.get_first_root_node()
        collections = {}
        for name in (MEMBERS_COLLECTION, PUBLIC_COLLECTION):
            existing = root.get_children().filter(name=name).first()
            if existing:
                self.stdout.write(f"  [ok] Collection « {name} » existante")
            else:
                existing = root.add_child(name=name)
                self.stdout.write(self.style.SUCCESS(f"  [créé] Collection « {name} »"))
            collections[name] = existing
        return collections[MEMBERS_COLLECTION]

    def _ensure_members_restriction(self, home, members, password):
        """Mot de passe des membres sur la racine privée et sur la collection « Espace membres »."""
        targets = [
            (PageViewRestriction, {"page": home}, f"page « {home.title} »"),
            (
                CollectionViewRestriction,
                {"collection": members},
                f"collection « {members.name} »",
            ),
        ]
        for model, lookup, label in targets:
            if model.objects.filter(**lookup).exists():
                self.stdout.write(f"  [ok] Restriction déjà posée sur la {label}")
            elif password:
                model.objects.create(
                    restriction_type=BaseViewRestriction.PASSWORD,
                    password=password,
                    **lookup,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"  [créé] Mot de passe membres sur la {label}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  [ATTENTION] Aucune restriction sur la {label} : son contenu est public. "
                        "Relancez avec --members-password ou utilisez « Confidentialité » dans l'admin."
                    )
                )

    def _ensure_public_site(self, options):
        hostname = options["public_hostname"]
        port = options["public_port"] or options["port"]
        site_name = options["public_site_name"] or options["site_name"]

        site = Site.objects.filter(hostname=hostname, port=port).first()
        if site:
            self.stdout.write(f"  [ok] Site public {hostname}:{port} existant")
            public_root = site.root_page.specific
        else:
            root = Page.objects.filter(depth=1).first()
            public_root = self._ensure_child(
                root,
                ContentPage,
                title="Accueil",
                slug="public",
                template_variant="standard",
            )
            site = Site.objects.create(
                hostname=hostname,
                port=port,
                site_name=site_name,
                root_page=public_root,
                is_default_site=False,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  [créé] Site public « {site_name} » sur {hostname}:{port}"
                )
            )

        self._ensure_child(
            public_root, ContentPage, title="Formulaires", slug="formulaires"
        )

        # for_site() crée les réglages à la volée : on teste l'existence avant.
        if not NavigationSettings.objects.filter(site=site).exists():
            NavigationSettings.objects.create(site=site, site_name=site_name)
            self.stdout.write(
                self.style.SUCCESS("  [créé] NavigationSettings du site public")
            )

        if not SecuritySettings.objects.filter(site=site).exists():
            SecuritySettings.objects.create(site=site, allow_indexing=True)
            self.stdout.write(
                self.style.SUCCESS("  [créé] Indexation autorisée sur le site public")
            )

        return site

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
            nav.menu_items.filter(link_page__isnull=False).values_list(
                "link_page_id", flat=True
            )
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
