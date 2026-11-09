from wagtail import blocks

from apps.interaction.models.forms import ORIGIN_FIELD


class FormBlock(blocks.PageChooserBlock):
    """
    Intègre une page « Formulaire » dans une section. Le formulaire est envoyé à la page
    formulaire elle-même (traitement et confidentialité natifs), qui renvoie ensuite
    vers la page d'origine avec le message de confirmation.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, page_type="interaction.FormPage", **kwargs)

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        form_page = value.specific if value else None
        if form_page is None or not form_page.live:
            ctx["form_page"] = None
            return ctx

        parent_context = parent_context or {}
        request = parent_context.get("request")
        page = parent_context.get("page")
        ctx["form_page"] = form_page
        ctx["form"] = form_page.get_form(
            page=form_page,
            user=getattr(request, "user", None),
            initial={ORIGIN_FIELD: page.pk} if page else None,
        )
        return ctx

    class Meta:
        icon = "form"
        label = "Formulaire"
        template = "blocks/form_block.html"
