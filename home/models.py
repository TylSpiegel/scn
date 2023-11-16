from django.db import models
from wagtail.models import Page

from choristes.models import CalendrierPublicEventPage

class HomePage(Page):

    def get_public_events(self):
        events = CalendrierPublicEventPage.objects.order_by('date').live()
        return events
