import json
from datetime import datetime, time

from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField

from apps.community.constants import VOICE_PART_CHOICES


class ChoristesIndexPage(Page):
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from .member import Choriste
        pupitre_order = {pupitre[0]: idx for idx, pupitre in enumerate(VOICE_PART_CHOICES)}
        choristes = Choriste.objects.all()
        choristes_sorted = sorted(
            choristes,
            key=lambda c: (pupitre_order.get(c.pupitre, 999), c.name)
        )
        context['choristes'] = choristes_sorted
        return context

    class Meta:
        verbose_name = "Page choristes"
        verbose_name_plural = "Pages choristes"


class CalendrierPage(Page):
    how_many_events = models.IntegerField(
        blank=True, null=True, default=5,
        help_text="Définir combien d'événements afficher dans la liste des prochains événements."
    )
    show_calendar = models.BooleanField(
        default=True,
        help_text="Est-ce que vous voulez que le widget calendrier s'affiche ?"
    )
    comment = RichTextField(
        blank=True,
        help_text="Un espace pour ajouter des commentaires : les changements récents, les prochaines dates..."
    )

    content_panels = Page.content_panels + [
        FieldPanel('comment'),
        FieldPanel('show_calendar'),
        FieldPanel('how_many_events'),
    ]

    def get_all_events(self):
        from .event import Event
        events = Event.objects.prefetch_related('tags').order_by('start_date').all()
        events_list = []
        for event in events:
            is_all_day = event.time_tbd or not event.start_time
            if is_all_day:
                start = event.start_date.strftime('%Y-%m-%d')
                end_date = event.end_date if event.end_date else event.start_date
                end = end_date.strftime('%Y-%m-%d')
            else:
                start = datetime.combine(event.start_date, event.start_time).strftime('%Y-%m-%dT%H:%M:%S')
                end_date = event.end_date if event.end_date else event.start_date
                end = datetime.combine(end_date, event.end_time).strftime('%Y-%m-%dT%H:%M:%S') if event.end_time else None
            events_list.append({
                'title': event.name,
                'start': start,
                'end': end,
                'allDay': is_all_day,
                'location': event.lieu or '',
                'color': '#3273dc',
                'tags': [str(tag) for tag in event.tags.all()],
                'time_tbd': event.time_tbd,
                'short_description': event.short_description or '',
                'long_description': event.long_description or '',
            })
        return json.dumps(events_list)

    def get_next_events(self):
        from .event import Event
        today = datetime.today().date()
        upcoming = Event.objects.filter(start_date__gte=today).order_by('start_date', 'start_time')
        return upcoming[0:self.how_many_events]

    def clean(self):
        if self.how_many_events is not None and self.how_many_events < 1:
            self.how_many_events = 0

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Calendrier"
        verbose_name_plural = "Calendriers"
