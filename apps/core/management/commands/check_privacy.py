"""
Contrôle en lecture seule de la séparation public / privé.

Usage :
    python manage.py check_privacy

Signale :
- les racines privées (HomePage) sans mot de passe ;
- les pages propres au privé rangées ailleurs que sous une HomePage ;
- les pages publiques qui affichent un événement, un morceau ou un formulaire privé ;
- les documents rangés hors d'une collection protégée et hors de « Public ».

Sort en erreur s'il y a au moins un problème bloquant (à lancer avant chaque déploiement).
"""

from django.core.management.base import BaseCommand, CommandError
from wagtail.documents import get_document_model
from wagtail.models import Collection, Site

from apps.community.models.pages import CalendrierPage, ChoristesIndexPage
from apps.content.models import ContentPage, HomePage, private_content_in
from apps.music.models import PieceIndexPage, RepertoirePage

PUBLIC_COLLECTION = "Public"
PRIVATE_PAGE_MODELS = (
    CalendrierPage,
    ChoristesIndexPage,
    PieceIndexPage,
    RepertoirePage,
)


class Command(BaseCommand):
    help = "Vérifie que le contenu privé n'est pas exposé sur un site public."

    def handle(self, *args, **options):
        errors = []
        warnings = []

        for site in Site.objects.select_related("root_page"):
            root = site.root_page.specific
            restricted = root.get_view_restrictions().exists()
            if isinstance(root, HomePage) and not restricted:
                errors.append(
                    f"Site privé {site} : la racine « {root.title} » n'a pas de mot de passe."
                )
            self.stdout.write(
                f"  Site {site} : racine {type(root).__name__}, {'privée' if restricted else 'publique'}"
            )

        for model in PRIVATE_PAGE_MODELS:
            for page in model.objects.all():
                if not isinstance(page.get_parent().specific, HomePage):
                    errors.append(
                        f"{model.__name__} « {page.title} » n'est pas rangée sous une HomePage."
                    )

        for page in ContentPage.objects.all():
            if page.get_view_restrictions().exists():
                continue
            found = private_content_in(page.body)
            if found:
                errors.append(
                    f"Page publique « {page.title} » ({page.url_path}) : {' ; '.join(found)}."
                )

        for collection in Collection.objects.all():
            documents = get_document_model().objects.filter(collection=collection)
            if not documents.exists():
                continue
            if (
                collection.name == PUBLIC_COLLECTION
                or collection.get_view_restrictions().exists()
            ):
                continue
            warnings.append(
                f"Collection « {collection.name} » sans restriction : {documents.count()} document(s) "
                "accessibles à tous."
            )

        for message in warnings:
            self.stdout.write(self.style.WARNING(f"  [ATTENTION] {message}"))
        for message in errors:
            self.stdout.write(self.style.ERROR(f"  [ERREUR] {message}"))

        if errors:
            raise CommandError(f"{len(errors)} problème(s) de confidentialité.")
        self.stdout.write(
            self.style.SUCCESS("Aucun problème de confidentialité détecté.")
        )
