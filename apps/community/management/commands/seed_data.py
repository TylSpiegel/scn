from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wagtail.models import Page, Site
from datetime import datetime, timedelta, time
import random

from apps.community.models import Choriste, Event, Role
from apps.community.models.pages import CalendrierPage, ChoristesIndexPage
from apps.music.models import Piece, RepertoirePage
from apps.content.models import HomePage, ContentPage


class Command(BaseCommand):
    help = 'Seed database with mock data'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Creating mock data...')
        self.create_superuser()
        self.create_pages()
        self.create_pieces()
        self.create_repertoire()
        self.create_choristes()
        self.create_events()

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
        self.stdout.write(self.style.SUCCESS('Login: admin / admin'))

    def clear_data(self):
        Choriste.objects.all().delete()
        Event.objects.all().delete()
        Role.objects.all().delete()
        Piece.objects.all().delete()
        RepertoirePage.objects.all().delete()
        CalendrierPage.objects.all().delete()
        ChoristesIndexPage.objects.all().delete()
        ContentPage.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Data cleared'))

    def create_superuser(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(username='admin', email='admin@example.com', password='admin')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin'))

    def create_pages(self):
        home = HomePage.objects.first()
        if not home:
            root = Page.objects.get(id=1)
            home = HomePage(
                title="Accueil",
                name="Société Chorale de Namur",
                header="Bienvenue sur notre site",
                body="<p>Nous sommes une chorale passionnée.</p>",
                slug="accueil",
                show_in_menus=False
            )
            root.add_child(instance=home)
            self.stdout.write(self.style.SUCCESS(f'Created HomePage: {home.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'Using existing HomePage: {home.title}'))

        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            Site.objects.create(
                hostname='localhost', port=8000,
                site_name='Chorale SCN', root_page=home, is_default_site=True
            )
        elif site.root_page != home:
            site.root_page = home
            site.save()

        if not RepertoirePage.objects.exists():
            repertoire = RepertoirePage(
                title="Notre Répertoire",
                introduction="Découvrez notre répertoire musical",
                slug="repertoire", show_in_menus=True
            )
            home.add_child(instance=repertoire)
            self.stdout.write(self.style.SUCCESS('Created RepertoirePage'))

        if not CalendrierPage.objects.exists():
            calendrier = CalendrierPage(
                title="Calendrier",
                comment="<p>Retrouvez tous nos événements ici.</p>",
                show_calendar=True, how_many_events=5,
                slug="calendrier", show_in_menus=True
            )
            home.add_child(instance=calendrier)
            self.stdout.write(self.style.SUCCESS('Created CalendrierPage'))

        if not ChoristesIndexPage.objects.exists():
            choristes_page = ChoristesIndexPage(
                title="Nos Choristes", slug="choristes", show_in_menus=True
            )
            home.add_child(instance=choristes_page)
            self.stdout.write(self.style.SUCCESS('Created ChoristesIndexPage'))

    def create_pieces(self):
        pieces_data = [
            {
                'titre': 'Ave Verum Corpus', 'compositeur': 'Mozart',
                'descr': '<p>Motet sacré en ré majeur composé en 1791.</p>',
                'traduction': '<p><strong>Latin:</strong> Ave verum corpus natum</p>',
                'interpretation': '<p>Chanter avec douceur et dévotion.</p>'
            },
            {
                'titre': 'Hallelujah', 'compositeur': 'Leonard Cohen / arr. Cohn',
                'descr': '<p>Adaptation chorale du classique de Leonard Cohen.</p>',
                'traduction': '<p>I heard there was a secret chord</p>',
                'interpretation': '<p>Construire progressivement l\'intensité.</p>'
            },
            {
                'titre': 'Les Champs-Élysées', 'compositeur': 'Joe Dassin / arr. Lawson',
                'descr': '<p>Arrangement swing de ce classique français.</p>',
                'traduction': '<p>Je m\'baladais sur l\'avenue</p>',
                'interpretation': '<p>Rythme enlevé à ♩= 120.</p>'
            },
            {
                'titre': 'O Fortuna', 'compositeur': 'Carl Orff',
                'descr': '<p>Mouvement d\'ouverture des Carmina Burana.</p>',
                'traduction': '<p><strong>Latin:</strong> O Fortuna, velut luna</p>',
                'interpretation': '<p>Attaque forte et précise.</p>'
            },
            {
                'titre': 'Va pensiero', 'compositeur': 'Giuseppe Verdi',
                'descr': '<p>Le chœur des esclaves hébreux extrait de Nabucco.</p>',
                'traduction': '<p><strong>Italien:</strong> Va, pensiero, sull\'ali dorate</p>',
                'interpretation': '<p>Chanter avec nostalgie et espoir.</p>'
            },
            {
                'titre': 'Bohemian Rhapsody', 'compositeur': 'Queen / arr. Mark Brymer',
                'descr': '<p>Arrangement choral du chef-d\'œuvre de Queen.</p>',
                'traduction': '<p>Is this the real life?</p>',
                'interpretation': '<p>Changements de style nombreux.</p>'
            },
        ]

        for data in pieces_data:
            piece, created = Piece.objects.get_or_create(
                titre=data['titre'],
                defaults={
                    'compositeur': data['compositeur'],
                    'descr': data['descr'],
                    'traduction': data['traduction'],
                    'interpretation': data['interpretation'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Piece: {piece}'))

    def create_repertoire(self):
        from apps.music.models import RepertoireItem
        repertoire = RepertoirePage.objects.first()
        if not repertoire or repertoire.items.exists():
            return
        for i, piece in enumerate(Piece.objects.all()):
            RepertoireItem.objects.create(repertoire=repertoire, piece=piece, sort_order=i)
        self.stdout.write(self.style.SUCCESS(f'Linked {Piece.objects.count()} pieces to RepertoirePage'))

    def create_choristes(self):
        roles_data = ['Chef de chœur', 'Président', 'Trésorier', 'Secrétaire', 'Chef de pupitre']
        roles = {}
        for role_name in roles_data:
            role, _ = Role.objects.get_or_create(
                name=role_name, defaults={'description': f'Fonction de {role_name.lower()}'}
            )
            roles[role_name] = role

        pupitres = ['Soprano', 'Alto', 'Ténor', 'Basse']
        prenoms_f = ['Sophie', 'Marie', 'Julie', 'Claire', 'Emma', 'Laura', 'Camille', 'Léa', 'Alice', 'Chloé',
                     'Isabelle', 'Catherine', 'Nathalie', 'Valérie', 'Sylvie']
        prenoms_m = ['Pierre', 'Jean', 'Luc', 'Marc', 'Paul', 'Thomas', 'Nicolas', 'Antoine', 'Julien', 'Maxime',
                     'François', 'Philippe', 'Michel', 'Bernard', 'Olivier']
        noms = ['Dubois', 'Martin', 'Bernard', 'Petit', 'Robert', 'Richard', 'Durand', 'Leroy',
                'Moreau', 'Simon', 'Laurent', 'Lefebvre', 'Michel', 'Garcia', 'Roux', 'Vincent',
                'Fournier', 'Girard', 'Bonnet', 'Dupont', 'Lambert', 'Fontaine', 'Rousseau', 'Blanc']

        created_count = 0
        attempts = 0
        while created_count < 30 and attempts < 100:
            attempts += 1
            pupitre = random.choice(pupitres)
            prenom = random.choice(prenoms_f if pupitre in ['Soprano', 'Alto'] else prenoms_m)
            nom = random.choice(noms)
            full_name = f"{prenom} {nom}"
            if not Choriste.objects.filter(name=full_name).exists():
                choriste = Choriste.objects.create(
                    name=full_name, pupitre=pupitre,
                    mail=f"{prenom.lower()}.{nom.lower()}@example.com",
                    phone=f"0{random.randint(400, 499)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
                    birthdate=datetime(random.randint(1950, 2000), random.randint(1, 12), random.randint(1, 28)),
                    active=True
                )
                role_map = {0: 'Chef de chœur', 1: 'Président', 2: 'Trésorier', 3: 'Secrétaire'}
                if created_count in role_map:
                    choriste.choir_functions.add(roles[role_map[created_count]])
                elif created_count in [4, 8, 12, 16]:
                    choriste.choir_functions.add(roles['Chef de pupitre'])
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created_count} choristes'))

    def create_events(self):
        today = datetime.now().date()
        pupitres = ['Tutti', 'Soprano', 'Alto', 'Ténor', 'Basse']

        for i in range(5):
            days_ago = random.randint(7, 60)
            date = today - timedelta(days=days_ago)
            Event.objects.create(
                name=f"Répétition {date.strftime('%B')}",
                start_date=date, end_date=date,
                start_time=time(19, 30), end_time=time(21, 30),
                is_repetition=True, pupitre=random.choice(pupitres),
                lieu="Salle de répétition", adresse="Rue de la Musique 42, 5000 Namur"
            )

        event_types = [
            ('Répétition générale', True, 'Tutti', 'Salle de concert', time(19, 30), time(21, 30)),
            ('Concert de Printemps', False, 'Tutti', 'Église Saint-Loup', time(20, 0), time(22, 0)),
            ('Répétition Sopranos-Altos', True, 'Soprano', 'Salle de répétition', time(19, 30), time(21, 30)),
            ('Stage de chant', False, 'Tutti', 'Centre culturel', None, None),
            ('Répétition Ténors-Basses', True, 'Ténor', 'Salle de répétition', time(19, 30), time(21, 30)),
            ('Concert de Noël', False, 'Tutti', 'Cathédrale', time(20, 0), time(22, 0)),
            ('Répétition pupitres', True, 'Alto', 'Salle de répétition', time(19, 30), time(21, 30)),
            ('Anniversaire de la chorale', False, 'Tutti', 'Salle des fêtes', time(18, 0), time(23, 0)),
        ]

        for name, is_rep, pupitre, lieu, start_h, end_h in event_types:
            date = today + timedelta(days=random.randint(7, 120))
            Event.objects.create(
                name=name, start_date=date, end_date=date,
                start_time=start_h, end_time=end_h,
                time_tbd=(start_h is None), is_repetition=is_rep, pupitre=pupitre,
                lieu=lieu,
                adresse="Rue de la Musique 42, 5000 Namur" if is_rep else "Place Royale 1, 5000 Namur",
                description=f"{'Répétition' if is_rep else 'Concert'} pour {pupitre if pupitre != 'Tutti' else 'toute la chorale'}"
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(event_types) + 5} events'))
