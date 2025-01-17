
@register_snippet
class Event(models.Model):
    # Basic info
    event_type = models.ForeignKey(
         'EventType',
         null=True,
         blank=True,
         on_delete=models.SET_NULL,
         verbose_name="Type d'événement"
    )
    name = models.CharField("Nom", max_length=255)
    description = models.TextField("Description", blank=True)
    
    # Schedule
    start_date = models.DateField("Date de début")
    end_date = models.DateField("Date de fin", blank=True, null=True)
    all_day = models.BooleanField("Journée entière", default=False)
    start_time = models.TimeField("Heure de début", blank=True, null=True)
    end_time = models.TimeField("Heure de fin", blank=True, null=True)

    # Location
    location = models.CharField("Lieu", max_length=250, blank=True)
    address = models.CharField("Adresse", max_length=250, blank=True)

    # Content
    content = RichTextField("Contenu enrichi", blank=True)
    allow_comments = models.BooleanField("Autoriser les commentaires", default=True)    

    base_panels = [
         MultiFieldPanel([
              FieldPanel('event_type'),
              FieldPanel('name'),
              FieldPanel('description'),
         ], heading="Informations générales"),
         MultiFieldPanel([
              FieldPanel('start_date'),
              FieldPanel('end_date'),
              FieldPanel('all_day'),
              FieldPanel('start_time'),
              FieldPanel('end_time'),
         ], heading="Date et heure"),
         MultiFieldPanel([
              FieldPanel('location'),
              FieldPanel('address'),
         ], heading="Lieu"),
    ]

    content_panels = [
         FieldPanel('content'),
         FieldPanel('allow_comments')
    ]

    edit_handler = TabbedInterface([
         ObjectList(base_panels, heading='Informations'),
         ObjectList(content_panels, heading='Contenu'),
    ])

    def save(self, *args, **kwargs):
         if self.event_type and not self.pk:  # Only for new events
              self.name = self.name or self.event_type.name
              self.start_time = self.start_time or self.event_type.default_start_time
              self.end_time = self.end_time or self.event_type.default_end_time
              self.location = self.location or self.event_type.default_location
              self.address = self.address or self.event_type.default_address
              self.requires_attendance = self.event_type.requires_attendance
              self.section = self.section or (None if self.event_type.all_sections else self.section)
         super().save(*args, **kwargs)

    def __str__(self):
         event_type_name = self.event_type.name if self.event_type else "Autre"
         return f"{self.start_date.strftime('%d-%m-%Y')} - {event_type_name}: {self.name}"

    class Meta:
         ordering = ['start_date', 'start_time']
         verbose_name = "Événement"
         verbose_name_plural = "Événements"