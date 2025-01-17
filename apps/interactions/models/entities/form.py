

"""Models for customizable forms as snippets"""
from django.db import models
from django.core.mail import send_mail
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from wagtail.fields import RichTextField
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from django.utils.translation import gettext_lazy as _

FIELD_TYPES = [
    ('singleline', _('Texte court')),
    ('multiline', _('Texte long')),
    ('email', _('Email')),
    ('number', _('Nombre')),
    ('url', _('URL')),
    ('checkbox', _('Case à cocher')),
    ('radio', _('Boutons radio')),
    ('select', _('Liste déroulante')),
    ('multiselect', _('Sélection multiple')),
    ('date', _('Date')),
]

class FormField(models.Model):
    """A field within a form"""
    form = ParentalKey('CustomForm', related_name='fields', on_delete=models.CASCADE)
    label = models.CharField(max_length=255, verbose_name=_('Label'))
    field_type = models.CharField(
        max_length=16,
        choices=FIELD_TYPES,
        verbose_name=_('Type de champ')
    )
    required = models.BooleanField(default=True, verbose_name=_('Obligatoire'))
    choices = models.TextField(
        blank=True,
        help_text=_('Valeurs séparées par virgules. Pour les listes et boutons radio uniquement.')
    )
    default_value = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Valeur par défaut du champ')
    )
    help_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Texte d\'aide'),
        help_text=_('Texte explicatif affiché sous le champ')
    )
    order = models.IntegerField(default=0)

    panels = [
        FieldPanel('label'),
        FieldPanel('field_type'),
        FieldPanel('required'),
        FieldPanel('choices'),
        FieldPanel('default_value'),
        FieldPanel('help_text'),
        FieldPanel('order'),
    ]

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label} ({self.field_type})"

@register_snippet
class CustomForm(ClusterableModel):
    """A customizable form that can be reused across pages"""
    title = models.CharField(max_length=255, verbose_name=_('Titre'))
    description = RichTextField(
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Texte affiché au-dessus du formulaire')
    )
    submit_text = models.CharField(
        max_length=100,
        default=_('Envoyer'),
        verbose_name=_('Texte du bouton'),
        help_text=_('Texte affiché sur le bouton d\'envoi')
    )
    success_message = models.CharField(
        max_length=255,
        default=_('Merci pour votre réponse.'),
        verbose_name=_('Message de succès')
    )
    
    # Email settings
    send_email = models.BooleanField(
        default=False,
        verbose_name=_('Envoyer un email'),
        help_text=_('Envoyer les réponses par email')
    )
    to_email = models.EmailField(
        blank=True,
        verbose_name=_('Email destinataire'),
        help_text=_('Adresse email qui recevra les réponses')
    )
    email_subject = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Sujet de l\'email')
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('submit_text'),
        FieldPanel('success_message'),
        InlinePanel('fields', label=_('Champs du formulaire')),
        FieldPanel('send_email'),
        FieldPanel('to_email'),
        FieldPanel('email_subject'),
    ]

    def __str__(self):
        return self.title

class FormResponse(models.Model):
    """Stores a form submission"""
    form = models.ForeignKey(
        CustomForm,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    class Meta:
        ordering = ['-submitted_at']

    def send_email_notification(self):
        """Send email with form response if configured"""
        if not self.form.send_email or not self.form.to_email:
            return

        message = "Nouvelle réponse au formulaire:\n\n"
        for key, value in self.data.items():
            message += f"{key}: {value}\n"

        send_mail(
            subject=self.form.email_subject or f"Réponse: {self.form.title}",
            message=message,
            from_email=None,  # Uses DEFAULT_FROM_EMAIL
            recipient_list=[self.form.to_email],
        )