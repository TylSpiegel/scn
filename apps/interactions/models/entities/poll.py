from django.core.validators import MaxLengthValidator
from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel

@register_snippet
class PollOption(models.Model):
    """Options de réponse possibles, communes à toutes les questions du sondage"""
    poll = models.ForeignKey(
        'Poll',
        related_name='options',
        on_delete=models.CASCADE
    )
    text = models.CharField(
        max_length=255,
        verbose_name="Texte de l'option"
    )
    color = ColorField(
        default='#000000',
        verbose_name="Couleur de l'option"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    panels = [
        FieldPanel('text'),
        NativeColorPanel('color'),
        FieldPanel('order'),
    ]

    class Meta:
        ordering = ['order']
        verbose_name = "Option de réponse"
        verbose_name_plural = "Options de réponse"

    def __str__(self):
        return f"{self.text}"


class PollQuestion(models.Model):
    """Questions individuelles dans le sondage"""
    poll = models.ForeignKey(
        'Poll',
        related_name='questions',
        on_delete=models.CASCADE
    )
    text = models.CharField(
        max_length=255,
        verbose_name="Question"
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name="Réponse obligatoire"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    panels = [
        FieldPanel('text'),
        FieldPanel('is_required'),
        FieldPanel('order'),
    ]

    class Meta:
        ordering = ['order']
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.text


@register_snippet
class Poll(models.Model):
    """Sondage principal qui contient plusieurs questions"""
    VISIBILITY_CHOICES = (
        ('immediate', 'Immédiatement après avoir voté'),
        ('after_close', 'Uniquement après la fermeture du sondage'),
        ('never', 'Jamais'),
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Titre du sondage"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    is_closed = models.BooleanField(
        default=False,
        verbose_name="Sondage fermé"
    )
    show_results = models.BooleanField(
        default=False,
        verbose_name="Afficher les résultats"
    )
    results_visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='after_close',
        verbose_name="Visibilité des résultats"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('description'),
        ], heading="Informations générales"),
        MultiFieldPanel([
            FieldPanel('is_closed'),
            FieldPanel('show_results'),
            FieldPanel('results_visibility'),
        ], heading="Paramètres d'affichage"),
        InlinePanel('questions', label="Questions", max_num=20),
        InlinePanel('options', label="Options de réponse", max_num=10),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Sondage"
        verbose_name_plural = "Sondages"


class PollResponse(models.Model):
    """Réponses des utilisateurs pour chaque question"""
    poll = models.ForeignKey(
        Poll,
        related_name='responses',
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        PollQuestion,
        related_name='responses',
        on_delete=models.CASCADE
    )
    respondent_name = models.CharField(
        max_length=255,
        verbose_name="Nom du répondant"
    )
    selected_option = models.ForeignKey(
        PollOption,
        related_name='responses',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('poll', 'question', 'respondent_name')
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"

    def __str__(self):
        return f"{self.respondent_name} - {self.question} - {self.selected_option}"