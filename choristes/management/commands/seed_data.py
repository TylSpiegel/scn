from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wagtail.models import Page, Site
from datetime import datetime, timedelta, time
import random

# Importer depuis choristes
from choristes.models import (
    MorceauPage, MorceauIndexPage, CalendrierPage,
    ChoristesIndexPage, Choriste, Evenement, ChoirRole
)
from home.models import HomePage, ContentPage


class Command(BaseCommand):
    help = 'Seed database with mock data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('🧹 Clearing existing data...')
            self.clear_data()

        self.stdout.write('🌱 Creating mock data...')

        # Créer un superuser si nécessaire
        self.create_superuser()

        # Créer la structure de pages
        self.create_pages()

        # Créer des morceaux
        self.create_morceaux()

        # Créer des choristes
        self.create_choristes()

        # Créer des événements
        self.create_evenements()

        self.stdout.write(self.style.SUCCESS('✅ Successfully seeded database!'))
        self.stdout.write(self.style.SUCCESS('🔑 Login: admin / admin'))
        self.stdout.write(self.style.SUCCESS('🌐 Visit: http://127.0.0.1:8000/'))

    def clear_data(self):
        """Nettoyer les données existantes"""
        # Supprimer les snippets
        Choriste.objects.all().delete()
        Evenement.objects.all().delete()
        ChoirRole.objects.all().delete()

        # Supprimer les pages MorceauPage en premier (enfants)
        MorceauPage.objects.all().delete()

        # Puis les pages index et autres (mais PAS la HomePage si elle existe déjà)
        MorceauIndexPage.objects.all().delete()
        CalendrierPage.objects.all().delete()
        ChoristesIndexPage.objects.all().delete()
        ContentPage.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('✓ Data cleared'))

    def create_superuser(self):
        """Créer un superuser admin/admin"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
            self.stdout.write(self.style.SUCCESS('👤 Created superuser: admin/admin'))

    def create_pages(self):
        """Créer la structure de base des pages"""
        # Chercher une HomePage existante
        home = HomePage.objects.first()

        if not home:
            # Si pas de HomePage, la créer
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
            self.stdout.write(self.style.SUCCESS(f'🏠 Created HomePage: {home.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Using existing HomePage: {home.title}'))

        # Créer ou mettre à jour le Site
        site = Site.objects.filter(is_default_site=True).first()

        if not site:
            # Créer le site
            site = Site.objects.create(
                hostname='localhost',
                port=8000,
                site_name='Chorale SCN',
                root_page=home,
                is_default_site=True
            )
            self.stdout.write(self.style.SUCCESS(f'🌐 Created Site: {site.site_name}'))
        else:
            # Mettre à jour le site existant
            if site.root_page != home:
                site.root_page = home
                site.save()
                self.stdout.write(self.style.SUCCESS(f'🔧 Set HomePage as site root'))

        # MorceauIndexPage
        if not MorceauIndexPage.objects.exists():
            morceau_index = MorceauIndexPage(
                title="Nos Chants",
                introduction="Découvrez notre répertoire musical",
                slug="chants",
                show_in_menus=True
            )
            home.add_child(instance=morceau_index)
            self.stdout.write(self.style.SUCCESS(f'🎵 Created MorceauIndexPage: {morceau_index.title}'))

        # CalendrierPage
        if not CalendrierPage.objects.exists():
            calendrier = CalendrierPage(
                title="Calendrier",
                comment="<p>Retrouvez tous nos événements ici.</p>",
                show_calendar=True,
                how_many_events=5,
                slug="calendrier",
                show_in_menus=True
            )
            home.add_child(instance=calendrier)
            self.stdout.write(self.style.SUCCESS(f'📅 Created CalendrierPage: {calendrier.title}'))

        # ChoristesIndexPage
        if not ChoristesIndexPage.objects.exists():
            choristes = ChoristesIndexPage(
                title="Nos Choristes",
                slug="choristes",
                show_in_menus=True
            )
            home.add_child(instance=choristes)
            self.stdout.write(self.style.SUCCESS(f'👥 Created ChoristesIndexPage: {choristes.title}'))

    def create_morceaux(self):
        """Créer des morceaux de musique"""
        morceau_index = MorceauIndexPage.objects.first()

        if not morceau_index:
            self.stdout.write(self.style.WARNING('⚠️  MorceauIndexPage not found, skipping morceaux'))
            return

        morceaux_data = [
            {
                'titre': 'Ave Verum Corpus',
                'compositeur': 'Mozart',
                'descr': '<p>Motet sacré en ré majeur composé en 1791. Une des dernières œuvres de Mozart, d\'une beauté et simplicité touchantes.</p>',
                'traduction': '<p><strong>Latin:</strong> Ave verum corpus natum<br>De Maria Virgine<br><br><strong>Français:</strong> Salut, vrai corps né<br>De la Vierge Marie</p>',
                'interpretation': '<p>Chanter avec douceur et dévotion. Attention aux nuances piano dans les mesures 5-8.</p>'
            },
            {
                'titre': 'Hallelujah',
                'compositeur': 'Leonard Cohen / arr. Cohn',
                'descr': '<p>Adaptation chorale du célèbre classique de Leonard Cohen. Arrangement en quatre voix avec sections en solo et tutti.</p>',
                'traduction': '<p>I heard there was a secret chord<br>That David played and it pleased the Lord<br><br>J\'ai entendu qu\'il existait un accord secret<br>Que David jouait et qui plaisait au Seigneur</p>',
                'interpretation': '<p>Construire progressivement l\'intensité. Les sopranos doivent rester légères dans les aigus du refrain.</p>'
            },
            {
                'titre': 'Les Champs-Élysées',
                'compositeur': 'Joe Dassin / arr. Lawson',
                'descr': '<p>Arrangement swing de ce classique de la chanson française. Version rythmée et enjouée parfaite pour les concerts.</p>',
                'traduction': '<p>Je m\'baladais sur l\'avenue<br>Le cœur ouvert à l\'inconnu<br>J\'avais envie de dire bonjour<br>À n\'importe qui</p>',
                'interpretation': '<p>Rythme enlevé à ♩= 120. Les hommes marquent le beat sur les temps 2 et 4.</p>'
            },
            {
                'titre': 'O Fortuna',
                'compositeur': 'Carl Orff',
                'descr': '<p>Mouvement d\'ouverture des Carmina Burana. Pièce dramatique et puissante qui évoque la roue de la fortune.</p>',
                'traduction': '<p><strong>Latin:</strong> O Fortuna, velut luna<br>Statu variabilis<br><br><strong>Français:</strong> Ô Fortune, comme la lune<br>Tu es changeante</p>',
                'interpretation': '<p>Attaque forte et précise. Les consonnes doivent être tranchantes. Respecter scrupuleusement les nuances fff et pp.</p>'
            },
            {
                'titre': 'Va pensiero',
                'compositeur': 'Giuseppe Verdi',
                'descr': '<p>Le chœur des esclaves hébreux extrait de l\'opéra Nabucco. Hymne à la liberté devenu un symbole de l\'identité italienne.</p>',
                'traduction': '<p><strong>Italien:</strong> Va, pensiero, sull\'ali dorate<br>Va, ti posa sui clivi, sui colli<br><br><strong>Français:</strong> Va, pensée, sur tes ailes dorées<br>Va, pose-toi sur les pentes, sur les collines</p>',
                'interpretation': '<p>Chanter avec nostalgie et espoir. Les phrases doivent être longues et legato. Respiration collective aux virgules.</p>'
            },
            {
                'titre': 'Bohemian Rhapsody',
                'compositeur': 'Queen / arr. Mark Brymer',
                'descr': '<p>Arrangement choral du chef-d\'œuvre de Queen. Six minutes d\'intensité rock mêlant opéra, ballade et hard rock.</p>',
                'traduction': '<p>Is this the real life?<br>Is this just fantasy?<br><br>Est-ce la vraie vie?<br>Est-ce juste un fantasme?</p>',
                'interpretation': '<p>Changements de style nombreux. La section "opera" requiert une grande précision rythmique.</p>'
            },
        ]

        for data in morceaux_data:
            if not MorceauPage.objects.filter(titre=data['titre']).exists():
                morceau = MorceauPage(
                    title=f"{data['titre']} - {data['compositeur']}",
                    titre=data['titre'],
                    compositeur=data['compositeur'],
                    descr=data['descr'],
                    traduction=data['traduction'],
                    interpretation=data['interpretation'],
                    activer_timecodes=False,
                    slug=data['titre'].lower().replace(' ', '-').replace("'", '').replace(',', '').replace('&', 'and')
                )
                morceau_index.add_child(instance=morceau)
                self.stdout.write(self.style.SUCCESS(f'♪ Created Morceau: {morceau.titre}'))

    def create_choristes(self):
        """Créer des choristes"""
        # Créer les rôles
        roles_data = ['Chef de chœur', 'Président', 'Trésorier', 'Secrétaire', 'Chef de pupitre']
        roles = {}

        for role_name in roles_data:
            role, created = ChoirRole.objects.get_or_create(
                name=role_name,
                defaults={'description': f'Fonction de {role_name.lower()}'}
            )
            roles[role_name] = role
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created Role: {role_name}'))

        # Créer des choristes
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
        max_attempts = 100

        while created_count < 30 and attempts < max_attempts:
            attempts += 1
            pupitre = random.choice(pupitres)

            if pupitre in ['Soprano', 'Alto']:
                prenom = random.choice(prenoms_f)
            else:
                prenom = random.choice(prenoms_m)

            nom = random.choice(noms)
            full_name = f"{prenom} {nom}"

            if not Choriste.objects.filter(name=full_name).exists():
                choriste = Choriste.objects.create(
                    name=full_name,
                    pupitre=pupitre,
                    mail=f"{prenom.lower()}.{nom.lower()}@example.com",
                    phone=f"0{random.randint(400, 499)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
                    birthdate=datetime(
                        random.randint(1950, 2000),
                        random.randint(1, 12),
                        random.randint(1, 28)
                    ),
                    active=True
                )

                # Attribuer des rôles à quelques choristes
                if created_count == 0:
                    choriste.choir_functions.add(roles['Chef de chœur'])
                elif created_count == 1:
                    choriste.choir_functions.add(roles['Président'])
                elif created_count == 2:
                    choriste.choir_functions.add(roles['Trésorier'])
                elif created_count == 3:
                    choriste.choir_functions.add(roles['Secrétaire'])
                elif created_count in [4, 8, 12, 16]:
                    choriste.choir_functions.add(roles['Chef de pupitre'])

                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'👤 Created {created_count} choristes'))


def create_evenements(self):
    """Créer des événements"""
    today = datetime.now().date()
    pupitres = ['Tutti', 'Soprano', 'Alto', 'Ténor', 'Basse']

    # Événements passés
    for i in range(5):
        days_ago = random.randint(7, 60)
        date = today - timedelta(days=days_ago)

        Evenement.objects.create(
            name=f"Répétition {date.strftime('%B')}",
            start_date=date,
            end_date=date,
            start_time=time(19, 30),
            end_time=time(21, 30),
            is_repetition=True,
            pupitre=random.choice(pupitres),
            lieu="Salle de répétition",
            adresse="Rue de la Musique 42, 5000 Namur"
        )

    # Événements futurs
    event_types = [
        ('Répétition générale', True, 'Tutti', 'Salle de concert', time(19, 30), time(21, 30)),
        ('Concert de Printemps', False, 'Tutti', 'Église Saint-Loup', time(20, 0), time(22, 0)),
        ('Répétition Sopranos-Altos', True, 'Soprano', 'Salle de répétition', time(19, 30), time(21, 30)),
        ('Stage de chant', False, 'Tutti', 'Centre culturel', None, None),  # Heure TBD
        ('Répétition Ténors-Basses', True, 'Ténor', 'Salle de répétition', time(19, 30), time(21, 30)),
        ('Concert de Noël', False, 'Tutti', 'Cathédrale', time(20, 0), time(22, 0)),
        ('Répétition pupitres', True, 'Alto', 'Salle de répétition', time(19, 30), time(21, 30)),
        ('Anniversaire de la chorale', False, 'Tutti', 'Salle des fêtes', time(18, 0), time(23, 0)),
    ]

    for name, is_rep, pupitre, lieu, start_h, end_h in event_types:
        days_ahead = random.randint(7, 120)
        date = today + timedelta(days=days_ahead)

        Evenement.objects.create(
            name=name,
            start_date=date,
            end_date=date,
            start_time=start_h,
            end_time=end_h,
            time_tbd=(start_h is None),
            is_repetition=is_rep,
            pupitre=pupitre,
            lieu=lieu,
            adresse="Rue de la Musique 42, 5000 Namur" if is_rep else "Place Royale 1, 5000 Namur",
            description=f"{'Répétition' if is_rep else 'Concert'} pour {pupitre if pupitre != 'Tutti' else 'toute la chorale'}"
        )

    self.stdout.write(self.style.SUCCESS(f'📅 Created {len(event_types) + 5} events'))
