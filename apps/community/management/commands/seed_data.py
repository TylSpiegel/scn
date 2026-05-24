from datetime import date, timedelta, time
import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wagtail.models import Page, Site

from apps.community.models import Choriste, Event, Role
from apps.community.models.pages import CalendrierPage, ChoristesIndexPage
from apps.music.models import Piece, PieceIndexPage, RepertoirePage
from apps.content.models import HomePage


class Command(BaseCommand):
    help = 'Seed database with mock data for development'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            self._clear()
        self._create_superuser()
        self._create_pages()
        self._create_pieces()
        self._create_repertoire()
        self._create_choristes()
        self._create_events()
        self.stdout.write(self.style.SUCCESS('Seed terminé ! Login : admin / admin'))

    # ------------------------------------------------------------------ #
    # Clear                                                                #
    # ------------------------------------------------------------------ #

    def _clear(self):
        self.stdout.write('Suppression des données existantes…')
        Event.objects.all().delete()
        Choriste.objects.all().delete()
        Role.objects.all().delete()

    # ------------------------------------------------------------------ #
    # Superuser                                                            #
    # ------------------------------------------------------------------ #

    def _create_superuser(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Superuser admin/admin créé'))

    # ------------------------------------------------------------------ #
    # Pages Wagtail                                                        #
    # ------------------------------------------------------------------ #

    def _create_pages(self):
        home = HomePage.objects.first()
        if not home:
            root = Page.objects.filter(depth=1).first()
            home = HomePage(
                title="Accueil", slug="accueil",
                name="Société Chorale de Namur",
                header="Bienvenue sur notre site",
                body="<p>Nous sommes une chorale passionnée.</p>",
                show_in_menus=False,
            )
            root.add_child(instance=home)
            self.stdout.write(self.style.SUCCESS('HomePage créée'))

        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            Site.objects.create(
                hostname='localhost', port=8000,
                site_name='Chorale SCN', root_page=home, is_default_site=True,
            )
        elif site.root_page_id != home.pk:
            site.root_page = home
            site.save()

        if not CalendrierPage.objects.exists():
            home.add_child(instance=CalendrierPage(
                title="Calendrier", slug="calendrier", show_in_menus=True,
                comment="<p>Retrouvez tous nos événements ici.</p>",
                show_calendar=True, how_many_events=5,
            ))
            self.stdout.write(self.style.SUCCESS('CalendrierPage créée'))

        if not ChoristesIndexPage.objects.exists():
            home.add_child(instance=ChoristesIndexPage(
                title="Choristes", slug="choristes", show_in_menus=True,
            ))
            self.stdout.write(self.style.SUCCESS('ChoristesIndexPage créée'))

        if not RepertoirePage.objects.exists():
            home.add_child(instance=RepertoirePage(
                title="Notre Répertoire", slug="repertoire", show_in_menus=True,
                introduction="Découvrez notre répertoire musical",
            ))
            self.stdout.write(self.style.SUCCESS('RepertoirePage créée'))

        if not PieceIndexPage.objects.exists():
            home.add_child(instance=PieceIndexPage(
                title="Morceaux", slug="morceaux", show_in_menus=True,
                introduction="Tous nos morceaux",
            ))
            self.stdout.write(self.style.SUCCESS('PieceIndexPage créée'))

    # ------------------------------------------------------------------ #
    # Morceaux (Piece = Page Wagtail)                                     #
    # ------------------------------------------------------------------ #

    def _create_pieces(self):
        index = PieceIndexPage.objects.first()
        if not index:
            return

        pieces = [
            dict(title='Ave Verum Corpus', compositeur='Mozart',
                 descr='<p>Motet sacré en ré majeur composé en 1791.</p>',
                 traduction='<p>Ave verum corpus natum de Maria Virgine.</p>',
                 interpretation='<p>Chanter avec douceur et dévotion. Tempo ♩= 60.</p>'),
            dict(title='Hallelujah', compositeur='Leonard Cohen / arr. Cohn',
                 descr='<p>Adaptation chorale du classique de Leonard Cohen.</p>',
                 traduction='<p>I heard there was a secret chord.</p>',
                 interpretation="<p>Construire progressivement l'intensité.</p>"),
            dict(title='Les Champs-Élysées', compositeur='Joe Dassin / arr. Lawson',
                 descr="<p>Arrangement swing de ce classique français.</p>",
                 traduction="<p>Je m'baladais sur l'avenue.</p>",
                 interpretation='<p>Rythme enlevé ♩= 120. Swing!</p>'),
            dict(title='O Fortuna', compositeur='Carl Orff',
                 descr="<p>Mouvement d'ouverture des Carmina Burana.</p>",
                 traduction='<p>O Fortuna, velut luna statu variabilis.</p>',
                 interpretation='<p>Attaque forte et précise.</p>'),
            dict(title='Va pensiero', compositeur='Giuseppe Verdi',
                 descr="<p>Le chœur des esclaves hébreux extrait de Nabucco.</p>",
                 traduction="<p>Va, pensiero, sull'ali dorate.</p>",
                 interpretation='<p>Chanter avec nostalgie et espoir.</p>'),
            dict(title='Bohemian Rhapsody', compositeur='Queen / arr. Mark Brymer',
                 descr="<p>Arrangement choral du chef-d'œuvre de Queen.</p>",
                 traduction='<p>Is this the real life? Is this just fantasy?</p>',
                 interpretation='<p>Nombreux changements de style — rester attentif au chef.</p>'),
        ]

        for data in pieces:
            if Piece.objects.filter(title=data['title']).exists():
                continue
            slug = (data['title'].lower()
                    .replace(' ', '-').replace("'", '').replace('é', 'e')
                    .replace('è', 'e').replace('ê', 'e')[:50])
            piece = Piece(slug=slug, **data)
            index.add_child(instance=piece)
            self.stdout.write(self.style.SUCCESS(f"Morceau créé : {piece}"))

    # ------------------------------------------------------------------ #
    # Répertoire                                                           #
    # ------------------------------------------------------------------ #

    def _create_repertoire(self):
        from apps.music.models import RepertoireItem
        repertoire = RepertoirePage.objects.first()
        if not repertoire or repertoire.items.exists():
            return
        for i, piece in enumerate(Piece.objects.all()):
            RepertoireItem.objects.create(
                repertoire=repertoire, piece=piece, sort_order=i,
            )
        self.stdout.write(self.style.SUCCESS(
            f'{Piece.objects.count()} morceaux liés au répertoire'
        ))

    # ------------------------------------------------------------------ #
    # Choristes                                                            #
    # ------------------------------------------------------------------ #

    def _create_choristes(self):
        roles_map = {}
        for name in ['Chef de chœur', 'Président', 'Trésorier', 'Secrétaire', 'Chef de pupitre']:
            role, _ = Role.objects.get_or_create(name=name)
            roles_map[name] = role

        pupitres_f = ['Soprano', 'Alto', 'Mezzo-soprano', 'Mezzo-alto']
        pupitres_m = ['Ténor', 'Basse']
        prenoms_f = ['Sophie', 'Marie', 'Julie', 'Claire', 'Emma', 'Laura',
                     'Camille', 'Léa', 'Alice', 'Chloé', 'Isabelle', 'Catherine',
                     'Nathalie', 'Valérie', 'Sylvie']
        prenoms_m = ['Pierre', 'Jean', 'Luc', 'Marc', 'Thomas', 'Nicolas',
                     'Antoine', 'Julien', 'Maxime', 'François', 'Philippe', 'Olivier']
        noms = ['Dubois', 'Martin', 'Bernard', 'Petit', 'Robert', 'Richard',
                'Durand', 'Leroy', 'Moreau', 'Simon', 'Laurent', 'Lefebvre',
                'Fontaine', 'Rousseau', 'Blanc', 'Lambert', 'Dupont']

        special_roles = {
            0: 'Chef de chœur', 1: 'Président', 2: 'Trésorier', 3: 'Secrétaire',
        }
        chef_pupitre_indices = {4, 9, 14, 19}

        created = 0
        attempts = 0
        while created < 30 and attempts < 200:
            attempts += 1
            is_female = random.random() < 0.6
            pupitre = random.choice(pupitres_f if is_female else pupitres_m)
            prenom = random.choice(prenoms_f if is_female else prenoms_m)
            nom = random.choice(noms)
            full_name = f"{prenom} {nom}"
            if Choriste.objects.filter(name=full_name).exists():
                continue

            year = random.randint(1955, 1998)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            choriste = Choriste.objects.create(
                name=full_name, pupitre=pupitre, active=True,
                mail=f"{prenom.lower()}.{nom.lower()}@example.com",
                phone=f"04{random.randint(70, 99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
                birthdate=date(year, month, day),
            )
            if created in special_roles:
                choriste.choir_functions.add(roles_map[special_roles[created]])
            elif created in chef_pupitre_indices:
                choriste.choir_functions.add(roles_map['Chef de pupitre'])

            choriste.addresses.create(
                street=f"Rue {random.choice(['de la Paix', 'du Midi', 'des Fleurs', 'Haute', 'Neuve'])} {random.randint(1, 80)}",
                zip_code=f"{random.choice(['5000', '5100', '5140', '5020'])}",
                city=random.choice(['Namur', 'Jambes', 'Beez', 'Bouge']),
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'{created} choristes créés'))

    # ------------------------------------------------------------------ #
    # Événements                                                           #
    # ------------------------------------------------------------------ #

    def _create_events(self):
        today = date.today()
        lieux_rep = [
            ('Salle paroissiale Saint-Loup', 'Rue du Collège 7, 5000 Namur'),
            ('Centre culturel de Namur', 'Avenue Golenvaux 14, 5000 Namur'),
        ]
        lieux_concert = [
            ('Église Saint-Loup', 'Rue du Collège, 5000 Namur'),
            ('Cathédrale Saint-Aubain', 'Place Saint-Aubain, 5000 Namur'),
            ('Salle des fêtes de Jambes', 'Chaussée de Liège 181, 5100 Namur'),
        ]

        # Événements passés (répétitions)
        for i in range(6):
            past_date = today - timedelta(days=random.randint(7, 90))
            lieu, adresse = random.choice(lieux_rep)
            Event.objects.create(
                name=f"Répétition — {past_date.strftime('%B %Y')}",
                start_date=past_date,
                start_time=time(19, 30),
                end_time=time(21, 30),
                lieu=lieu, adresse=adresse,
                description="Répétition hebdomadaire de l'ensemble de la chorale.",
            )

        # Événements futurs variés
        upcoming = [
            dict(name="Répétition générale",
                 delta=7, start_time=time(19, 30), end_time=time(22, 0),
                 lieu=lieux_rep[0][0], adresse=lieux_rep[0][1],
                 description="Répétition générale avant le concert de printemps."),
            dict(name="Concert de Printemps",
                 delta=21, start_time=time(20, 0), end_time=time(22, 0),
                 lieu=lieux_concert[0][0], adresse=lieux_concert[0][1],
                 description="Notre grand concert annuel de printemps."),
            dict(name="Répétition pupitres",
                 delta=14, start_time=time(19, 30), end_time=time(21, 30),
                 lieu=lieux_rep[1][0], adresse=lieux_rep[1][1],
                 description="Répétition par pupitre — sopranos et ténors."),
            dict(name="Stage de chant choral",
                 delta=35, start_time=None, end_time=None, time_tbd=True,
                 lieu="Centre Dominicain de Namur", adresse="Rue Basse-Marcelle 6, 5000 Namur",
                 description="Stage d'une journée avec un chef invité. Heure à confirmer."),
            dict(name="Répétition",
                 delta=49, start_time=time(19, 30), end_time=time(21, 30),
                 lieu=lieux_rep[0][0], adresse=lieux_rep[0][1],
                 description=None),
            dict(name="Concert de Noël",
                 delta=180, start_time=time(20, 0), end_time=time(22, 30),
                 lieu=lieux_concert[1][0], adresse=lieux_concert[1][1],
                 description="Concert de Noël à la cathédrale — entrée libre."),
            dict(name="Anniversaire de la chorale",
                 delta=210, start_time=time(18, 0), end_time=time(23, 0),
                 lieu=lieux_concert[2][0], adresse=lieux_concert[2][1],
                 description="Soirée de gala pour les 50 ans de la chorale."),
        ]

        for ev in upcoming:
            ev_date = today + timedelta(days=ev['delta'] + random.randint(-3, 3))
            Event.objects.create(
                name=ev['name'],
                start_date=ev_date,
                start_time=ev.get('start_time'),
                end_time=ev.get('end_time'),
                time_tbd=ev.get('time_tbd', False),
                lieu=ev.get('lieu'),
                adresse=ev.get('adresse'),
                description=ev.get('description'),
            )

        self.stdout.write(self.style.SUCCESS(
            f'{len(upcoming) + 6} événements créés'
        ))
