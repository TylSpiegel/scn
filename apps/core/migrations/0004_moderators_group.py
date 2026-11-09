"""
Groupe « Modérateurs » : accès à tout le contenu des deux sites (pages, documents, images,
snippets, réglages, formulaires et réponses, redirections), mais ni aux utilisateurs ni aux sites.
"""

from django.contrib.auth.management import create_permissions
from django.db import migrations

GROUP_NAME = "Modérateurs"

PAGE_PERMISSIONS = [
    "add_page",
    "change_page",
    "publish_page",
    "bulk_delete_page",
    "lock_page",
    "unlock_page",
]

COLLECTION_PERMISSIONS = [
    (
        "wagtaildocs",
        ["add_document", "change_document", "choose_document", "delete_document"],
    ),
    ("wagtailimages", ["add_image", "change_image", "choose_image", "delete_image"]),
]

# Toutes les permissions (ajout, modification, suppression, lecture) de ces modèles.
MODEL_PERMISSIONS = [
    ("community", ["event", "role", "choriste"]),
    ("core", ["navigationsettings", "themesettings", "securitysettings"]),
    ("wagtailforms", ["formsubmission"]),
    ("wagtailredirects", ["redirect"]),
]


def _ensure_permissions(apps):
    """Les permissions ne sont créées qu'après `migrate` : on les force ici (base neuve)."""
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def forwards(apps, schema_editor):
    _ensure_permissions(apps)

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    Page = apps.get_model("wagtailcore", "Page")
    Collection = apps.get_model("wagtailcore", "Collection")
    GroupPagePermission = apps.get_model("wagtailcore", "GroupPagePermission")
    GroupCollectionPermission = apps.get_model(
        "wagtailcore", "GroupCollectionPermission"
    )

    group, _ = Group.objects.get_or_create(name=GROUP_NAME)

    group.permissions.add(
        Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
    )
    for app_label, models in MODEL_PERMISSIONS:
        group.permissions.add(
            *Permission.objects.filter(
                content_type__app_label=app_label,
                content_type__model__in=models,
            )
        )

    root_page = Page.objects.filter(depth=1).first()
    if root_page:
        for permission in Permission.objects.filter(
            content_type__app_label="wagtailcore",
            codename__in=PAGE_PERMISSIONS,
        ):
            GroupPagePermission.objects.get_or_create(
                group=group, page=root_page, permission=permission
            )

    root_collection = Collection.objects.filter(depth=1).first()
    if root_collection:
        for app_label, codenames in COLLECTION_PERMISSIONS:
            for permission in Permission.objects.filter(
                content_type__app_label=app_label,
                codename__in=codenames,
            ):
                GroupCollectionPermission.objects.get_or_create(
                    group=group,
                    collection=root_collection,
                    permission=permission,
                )


def backwards(apps, schema_editor):
    apps.get_model("auth", "Group").objects.filter(name=GROUP_NAME).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_security_allow_indexing"),
        ("community", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("wagtailadmin", "0005_editingsession_is_editing"),
        ("wagtailcore", "0096_referenceindex_referenceindex_source_object_and_more"),
        ("wagtaildocs", "0014_alter_document_file_size"),
        ("wagtailforms", "0005_alter_formsubmission_form_data"),
        ("wagtailimages", "0027_image_description"),
        ("wagtailredirects", "0008_add_verbose_name_plural"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
