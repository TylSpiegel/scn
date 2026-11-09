"""
Chaque ContentSection devient un SectionBlock du StreamField ContentPage.body :
titre, date, puis contenu = texte riche suivi des références (événements, morceaux), dans l'ordre.

Les révisions des pages sont converties aussi : l'admin édite la dernière révision,
qui doit déjà contenir le nouveau `body`.
"""

import json
import uuid
from datetime import date

from django.db import migrations

REFERENCE_TYPES = ("event", "piece")


def _new_id():
    return str(uuid.uuid4())


def _load_stream(value):
    if not value:
        return []
    if isinstance(value, str):
        return json.loads(value)
    return list(value)


def section_to_block(title, section_date, body, references):
    """Données brutes d'un SectionBlock à partir des champs d'une ContentSection."""
    content = []
    if body:
        content.append({"type": "text", "value": body, "id": _new_id()})
    for ref in references:
        if ref.get("type") in REFERENCE_TYPES:
            content.append(
                {
                    "type": ref["type"],
                    "value": ref["value"],
                    "id": ref.get("id") or _new_id(),
                }
            )
    if isinstance(section_date, date):
        section_date = section_date.isoformat()
    return {
        "type": "section",
        "value": {"title": title, "date": section_date or None, "content": content},
        "id": _new_id(),
    }


def block_to_section(block):
    """Champs d'une ContentSection à partir d'un SectionBlock (les formulaires sont perdus)."""
    value = block["value"]
    content = value.get("content") or []
    return {
        "title": value.get("title") or "",
        "date": value.get("date") or date.today().isoformat(),
        "body": "".join(item["value"] for item in content if item["type"] == "text"),
        "references": [item for item in content if item["type"] in REFERENCE_TYPES],
    }


def _content_page_revisions(apps):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Revision = apps.get_model("wagtailcore", "Revision")
    content_type = ContentType.objects.filter(
        app_label="content", model="contentpage"
    ).first()
    if content_type is None:
        return Revision.objects.none()
    return Revision.objects.filter(content_type=content_type)


def forwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    ContentSection = apps.get_model("content", "ContentSection")

    for page in ContentPage.objects.all():
        body = [
            section_to_block(s.title, s.date, s.body, list(s.references.raw_data))
            for s in ContentSection.objects.filter(page=page).order_by(
                "sort_order", "pk"
            )
        ]
        ContentPage.objects.filter(pk=page.pk).update(body=body)

    for revision in _content_page_revisions(apps):
        content = revision.content
        sections = sorted(
            content.pop("sections", None) or [], key=lambda s: s.get("sort_order") or 0
        )
        body = [
            section_to_block(
                s.get("title", ""),
                s.get("date"),
                s.get("body", ""),
                _load_stream(s.get("references")),
            )
            for s in sections
        ]
        content["body"] = json.dumps(body)
        revision.content = content
        revision.save(update_fields=["content"])


def backwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    ContentSection = apps.get_model("content", "ContentSection")

    for page in ContentPage.objects.all():
        ContentSection.objects.filter(page=page).delete()
        for order, block in enumerate(_load_stream(list(page.body.raw_data))):
            ContentSection.objects.create(
                page=page, sort_order=order, **block_to_section(block)
            )

    for revision in _content_page_revisions(apps):
        content = revision.content
        blocks = _load_stream(content.pop("body", None))
        sections = []
        for order, block in enumerate(blocks):
            section = block_to_section(block)
            section["references"] = json.dumps(section["references"])
            sections.append(
                {
                    "pk": None,
                    "page": int(revision.object_id),
                    "sort_order": order,
                    **section,
                }
            )
        content["sections"] = sections
        revision.content = content
        revision.save(update_fields=["content"])


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0002_content_page_body"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("wagtailcore", "0096_referenceindex_referenceindex_source_object_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
