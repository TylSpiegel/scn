from django.core.management.base import BaseCommand
from choristes.models import Evenement
from datetime import datetime


class Command(BaseCommand):
    help = 'Migrer les anciennes données datetime vers date/time séparés'

    def handle(self, *args, **options):
        # Cette commande doit être exécutée AVANT d'appliquer la migration finale
        # qui supprime les champs temp
        
        events = Evenement.objects.all()
        
        for event in events:
            # Extraire date et heure depuis start_date_temp
            if hasattr(event, 'start_date_temp') and event.start_date_temp:
                event.start_date = event.start_date_temp.date()
                event.start_time = event.start_date_temp.time()
            
            # Extraire date et heure depuis end_date_temp
            if hasattr(event, 'end_date_temp') and event.end_date_temp:
                event.end_date = event.end_date_temp.date()
                event.end_time = event.end_date_temp.time()
            
            event.save()
            self.stdout.write(f'Migré: {event.name}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ {events.count()} événements migrés'))
