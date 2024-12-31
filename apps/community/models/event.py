


@register_snippet
class Evenement(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_repetition = models.BooleanField(default=True)
    pupitre = models.CharField(choices=PUPITRES_CHOICES, max_length=25)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True)
    start_hour = models.TimeField(null=True)
    end_hour = models.TimeField(null=True)
    lieu = models.CharField(null=True, blank=True, max_length=250)
    adresse = models.CharField(null=True, blank=True, max_length=250)

    panels = [
        FieldPanel('name'),
        FieldPanel('is_repetition'),
        FieldPanel('description'),
        FieldPanel('pupitre'),
        FieldPanel('start_date'),
        FieldPanel('start_hour'),
        FieldPanel('end_hour'),
        FieldPanel('lieu'),
        FieldPanel('adresse'),
    ]

    def __str__(self):
        return f"{self.start_date.strftime('%d-%m')} // {self.name} - {self.pupitre} "