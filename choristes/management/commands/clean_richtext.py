from django.core.management.base import BaseCommand
from choristes.models import MorceauPage
import re


class Command(BaseCommand):
    help = 'Nettoyer le HTML invalide dans les champs RichText'

    def clean_html(self, html):
        """Nettoie le HTML malformé"""
        if not html:
            return html
        
        # Remplacer <br> non fermé par <br/>
        html = re.sub(r'<br(?!\s*/>)', '<br/>', html)
        
        # Supprimer les <br> à l'intérieur des <p>
        html = re.sub(r'<p>([^<]*)<br\s*/?>\s*</p>', r'<p>\1</p>', html)
        
        # Fermer les tags ouverts
        # Si un <p> est suivi d'un </p> sans fermeture, on le garde
        # C'est un nettoyage basique, pour des cas plus complexes, utilisez BeautifulSoup
        
        return html

    def handle(self, *args, **options):
        cleaned_count = 0
        error_count = 0
        
        # Nettoyer MorceauPage
        for page in MorceauPage.objects.all():
            try:
                modified = False
                
                if page.descr:
                    old_descr = page.descr
                    page.descr = self.clean_html(page.descr)
                    if old_descr != page.descr:
                        modified = True
                        self.stdout.write(f'  Nettoyé descr: {page.title}')
                
                if page.traduction:
                    old_trad = page.traduction
                    page.traduction = self.clean_html(page.traduction)
                    if old_trad != page.traduction:
                        modified = True
                        self.stdout.write(f'  Nettoyé traduction: {page.title}')
                
                if page.interpretation:
                    old_interp = page.interpretation
                    page.interpretation = self.clean_html(page.interpretation)
                    if old_interp != page.interpretation:
                        modified = True
                        self.stdout.write(f'  Nettoyé interpretation: {page.title}')
                
                if modified:
                    page.save()
                    cleaned_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Nettoyé: {page.title}'))
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'✗ Erreur sur {page.title}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {cleaned_count} pages nettoyées'))
        if error_count:
            self.stdout.write(self.style.WARNING(f'⚠️  {error_count} erreurs'))
