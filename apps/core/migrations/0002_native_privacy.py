"""
Bascule de la protection maison (SecuritySettings.password + middleware) vers la
confidentialité native de Wagtail :
- collections « Espace membres » (restreinte) et « Public » ;
- restriction mot de passe sur la racine de chaque site qui avait un mot de passe ;
- documents de la collection racine déplacés dans « Espace membres ».
"""

from django.db import migrations

MEMBERS_COLLECTION = "Espace membres"
PUBLIC_COLLECTION = "Public"
PASSWORD = "password"

# Arbre treebeard (MP_Node) : chemins en base 36, 4 caractères par niveau.
STEPLEN = 4
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _to_step(number):
    step = ""
    while number:
        number, rest = divmod(number, len(ALPHABET))
        step = ALPHABET[rest] + step
    return step.rjust(STEPLEN, "0")


def _get_or_add_child(Collection, parent, name):
    children = Collection.objects.filter(
        path__startswith=parent.path, depth=parent.depth + 1
    )
    existing = children.filter(name=name).first()
    if existing:
        return existing
    last = children.order_by("-path").first()
    number = int(last.path[-STEPLEN:], 36) + 1 if last else 1
    child = Collection.objects.create(
        name=name,
        path=parent.path + _to_step(number),
        depth=parent.depth + 1,
        numchild=0,
    )
    parent.numchild += 1
    parent.save(update_fields=["numchild"])
    return child


def forwards(apps, schema_editor):
    Collection = apps.get_model("wagtailcore", "Collection")
    CollectionViewRestriction = apps.get_model(
        "wagtailcore", "CollectionViewRestriction"
    )
    PageViewRestriction = apps.get_model("wagtailcore", "PageViewRestriction")
    Document = apps.get_model("wagtaildocs", "Document")
    SecuritySettings = apps.get_model("core", "SecuritySettings")

    root = Collection.objects.filter(depth=1).first()
    if root is None:
        return

    members = _get_or_add_child(Collection, root, MEMBERS_COLLECTION)
    _get_or_add_child(Collection, root, PUBLIC_COLLECTION)

    protected = list(
        SecuritySettings.objects.exclude(password="").select_related("site")
    )
    for security in protected:
        PageViewRestriction.objects.get_or_create(
            page_id=security.site.root_page_id,
            restriction_type=PASSWORD,
            defaults={"password": security.password},
        )

    if protected:
        CollectionViewRestriction.objects.get_or_create(
            collection=members,
            restriction_type=PASSWORD,
            defaults={"password": protected[0].password},
        )

    Document.objects.filter(collection=root).update(collection=members)


def backwards(apps, schema_editor):
    Collection = apps.get_model("wagtailcore", "Collection")
    CollectionViewRestriction = apps.get_model(
        "wagtailcore", "CollectionViewRestriction"
    )
    PageViewRestriction = apps.get_model("wagtailcore", "PageViewRestriction")
    Document = apps.get_model("wagtaildocs", "Document")
    Image = apps.get_model("wagtailimages", "Image")
    SecuritySettings = apps.get_model("core", "SecuritySettings")

    for security in SecuritySettings.objects.select_related("site"):
        restriction = PageViewRestriction.objects.filter(
            page_id=security.site.root_page_id, restriction_type=PASSWORD
        ).first()
        if restriction:
            security.password = restriction.password
            security.save(update_fields=["password"])
            restriction.delete()

    root = Collection.objects.filter(depth=1).first()
    if root is None:
        return

    for name in (MEMBERS_COLLECTION, PUBLIC_COLLECTION):
        collection = Collection.objects.filter(depth=2, name=name).first()
        if collection is None:
            continue
        Document.objects.filter(collection=collection).update(collection=root)
        CollectionViewRestriction.objects.filter(collection=collection).delete()
        has_content = (
            collection.numchild or Image.objects.filter(collection=collection).exists()
        )
        if not has_content:
            collection.delete()
            root.numchild -= 1
            root.save(update_fields=["numchild"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
        ("wagtailcore", "0096_referenceindex_referenceindex_source_object_and_more"),
        ("wagtaildocs", "0014_alter_document_file_size"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
