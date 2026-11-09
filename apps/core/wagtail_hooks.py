from wagtail import hooks
from wagtail.models import BaseViewRestriction, PageViewRestriction
from wagtail.permission_policies import ModelPermissionPolicy
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from apps.core.models import Palette

PASSWORD = BaseViewRestriction.PASSWORD


def _can_access_admin(request):
    return request.user.has_perm("wagtailadmin.access_admin")


@hooks.register("before_serve_page", order=-1)
def let_editors_through_pages(page, request, serve_args, serve_kwargs):
    """Les comptes de l'admin voient les pages protégées sans saisir le mot de passe."""
    if not _can_access_admin(request):
        return
    for restriction in page.get_view_restrictions().filter(restriction_type=PASSWORD):
        restriction.mark_as_passed(request)


@hooks.register("before_serve_document", order=-1)
def share_members_password(document, request):
    """
    Un membre qui a déjà saisi le mot de passe des pages n'a pas à le ressaisir pour
    un document protégé par le même mot de passe. Passe avant le contrôle natif de Wagtail.
    """
    restrictions = document.collection.get_view_restrictions().filter(
        restriction_type=PASSWORD
    )
    if not restrictions:
        return

    if _can_access_admin(request):
        passed_passwords = None
    else:
        passed_ids = request.session.get(
            PageViewRestriction.passed_view_restrictions_session_key, []
        )
        passed_passwords = set(
            PageViewRestriction.objects.filter(
                id__in=passed_ids, restriction_type=PASSWORD
            ).values_list("password", flat=True)
        )
        if not passed_passwords:
            return

    for restriction in restrictions:
        if passed_passwords is None or restriction.password in passed_passwords:
            restriction.mark_as_passed(request)


class FixedSlotsPermissionPolicy(ModelPermissionPolicy):
    """Les palettes sont des emplacements fixes : on les modifie, on n'en ajoute ni n'en supprime."""

    def user_has_permission(self, user, action):
        if action in ("add", "delete"):
            return False
        return super().user_has_permission(user, action)

    def user_has_any_permission(self, user, actions):
        return any(self.user_has_permission(user, action) for action in actions)


class PaletteViewSet(SnippetViewSet):
    model = Palette
    icon = "image"
    menu_label = "Palettes"
    add_to_settings_menu = True
    list_display = ["name", "swatches", "used_by"]
    ordering = ["slot"]

    @property
    def permission_policy(self):
        return FixedSlotsPermissionPolicy(self.model)


register_snippet(PaletteViewSet)
