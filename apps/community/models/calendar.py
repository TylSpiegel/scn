



####                #####
#     CALENDRIER        #
####                #####

class CalendrierPage(Page):
    # OPTIONS

    # FIELDS
    how_many_events = models.IntegerField(blank=True, null=True, default=5, help_text="""
    Définir combien d'événements afficher dans la liste des prochains événements.""")

    show_calendar = models.BooleanField(default=True,
                                        help_text="""
    Est-ce que vous voulez que le widget calendrier s'affiche ? (max. 100)
    """,
                                        validators=[
                                            MinValueValidator(0),
                                            MaxValueValidator(100)
                                        ]
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
        events = Evenement.objects.order_by('start_date').all()
        events_list = [
            {
                'title': f'{event.name} {event.pupitre}' if event.is_repetition else f'{event.name}',
                'start': event.start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                'end': event.end_date.strftime("%Y-%m-%dT%H:%M:%S") if event.end_date else None,
                'color': self.get_event_color(event.pupitre),
            }
            for event in events
        ]
        return json.dumps(events_list)

    def get_event_color(self, pupitre):
        return PUPITRES_COLORS.get(pupitre, '#D3D3D3')

    def get_next_events(self):
        return Evenement.objects.filter(start_date__gt=timezone.now()).order_by('start_date').all()[
               0:self.how_many_events]

    def clean(self):
        if self.how_many_events < 1:
            self.how_many_events = 0

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


