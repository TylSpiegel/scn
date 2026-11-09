from django import forms
from django.contrib import messages
from django.db import models
from django.shortcuts import redirect
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.templatetags.wagtailcore_tags import richtext

# Champs ajoutés au formulaire généré, jamais enregistrés dans les réponses.
HONEYPOT_FIELD = "hp_website"
ORIGIN_FIELD = "origin_page"

DEFAULT_THANK_YOU = "Merci, votre réponse a bien été envoyée."


def _add_bulma_class(widget):
    if isinstance(widget, forms.Textarea):
        widget.attrs["class"] = "textarea"
    elif isinstance(widget, forms.widgets.Input) and widget.input_type not in (
        "checkbox",
        "radio",
        "hidden",
        "file",
    ):
        widget.attrs["class"] = "input"


class FormField(AbstractFormField):
    page = ParentalKey("FormPage", on_delete=models.CASCADE, related_name="form_fields")


class FormPage(AbstractEmailForm):
    """
    Formulaire natif Wagtail. Il hérite de la confidentialité de son emplacement :
    rangé sous la racine privée, il ne s'affiche et ne s'enregistre qu'avec le mot de passe.
    """

    intro = RichTextField(blank=True, verbose_name="Introduction")
    thank_you_text = RichTextField(
        blank=True,
        verbose_name="Message de confirmation",
        help_text="Affiché après l'envoi. Par défaut : « Merci, votre réponse a bien été envoyée. »",
    )

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Champs du formulaire"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            heading="Notification par e-mail (facultatif)",
        ),
    ]

    subpage_types = []

    class Meta:
        verbose_name = "Formulaire"
        verbose_name_plural = "Formulaires"

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields[HONEYPOT_FIELD] = forms.CharField(
            required=False,
            label="Laisser ce champ vide",
            widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
        )
        form.fields[ORIGIN_FIELD] = forms.IntegerField(
            required=False, widget=forms.HiddenInput
        )
        form.honeypot_name = HONEYPOT_FIELD
        for field in form.fields.values():
            _add_bulma_class(field.widget)
        return form

    def process_form_submission(self, form):
        trapped = form.cleaned_data.pop(HONEYPOT_FIELD, "")
        form.cleaned_data.pop(ORIGIN_FIELD, None)
        if trapped:
            # Robot : on fait comme si tout allait bien, sans rien enregistrer ni envoyer.
            return None
        return super().process_form_submission(form)

    def render_landing_page(self, request, form_submission=None, *args, **kwargs):
        origin = self._get_origin_page(request)
        if origin is None:
            return super().render_landing_page(
                request, form_submission, *args, **kwargs
            )

        message = (
            richtext(self.thank_you_text) if self.thank_you_text else DEFAULT_THANK_YOU
        )
        messages.success(request, message, extra_tags=self.message_tag)
        return redirect(f"{origin.get_url(request=request)}#{self.message_tag}")

    @property
    def message_tag(self):
        return f"form-{self.pk}"

    def _get_origin_page(self, request):
        """Page d'où le formulaire a été envoyé (bloc « Formulaire »), si elle est du même site."""
        if request.method != "POST":
            return None
        try:
            page_id = int(request.POST.get(ORIGIN_FIELD, ""))
        except ValueError:
            return None
        origin = Page.objects.live().filter(pk=page_id).first()
        if origin is None or origin.get_site() != self.get_site():
            return None
        return origin
