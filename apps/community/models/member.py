
####                            #####
#       CHORISTES SECTIONS          #
####                            #####

class ChoristesIndexPage(Page):
    max_count = 1

    def get_children(self):
        return Choriste.objects.order_by('pupitre').all()


@register_snippet
class Choriste(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    pupitre = models.CharField(choices=PUPITRES_CHOICES, max_length=25, null=True, blank=True)
    mail = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('pupitre'),
        FieldPanel('mail'),
        FieldPanel('phone')
    ]

    def __str__(self):
        return self.name


