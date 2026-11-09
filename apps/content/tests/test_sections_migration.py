from datetime import date
from importlib import import_module

from django.test import SimpleTestCase

migration = import_module("apps.content.migrations.0003_sections_to_body")


class SectionsMigrationTests(SimpleTestCase):
    """Conversion ContentSection <-> SectionBlock (migration content.0003)."""

    def test_section_becomes_block_with_text_then_references(self):
        references = [
            {
                "type": "event",
                "value": {"event": 3, "extra_content": "<p>x</p>"},
                "id": "e1",
            },
            {"type": "piece", "value": 7, "id": "p1"},
        ]
        block = migration.section_to_block(
            "Titre", date(2025, 1, 2), "<p>Corps</p>", references
        )

        self.assertEqual(block["type"], "section")
        value = block["value"]
        self.assertEqual(value["title"], "Titre")
        self.assertEqual(value["date"], "2025-01-02")
        self.assertEqual(
            [(item["type"], item["value"]) for item in value["content"]],
            [
                ("text", "<p>Corps</p>"),
                ("event", {"event": 3, "extra_content": "<p>x</p>"}),
                ("piece", 7),
            ],
        )
        self.assertEqual(value["content"][1]["id"], "e1")

    def test_empty_body_adds_no_text_block(self):
        block = migration.section_to_block("Titre", "2025-01-02", "", [])
        self.assertEqual(block["value"]["content"], [])

    def test_round_trip(self):
        references = [{"type": "piece", "value": 7, "id": "p1"}]
        block = migration.section_to_block(
            "Titre", date(2025, 1, 2), "<p>Corps</p>", references
        )
        self.assertEqual(
            migration.block_to_section(block),
            {
                "title": "Titre",
                "date": "2025-01-02",
                "body": "<p>Corps</p>",
                "references": references,
            },
        )

    def test_reverse_drops_forms(self):
        block = {
            "type": "section",
            "value": {
                "title": "T",
                "date": None,
                "content": [
                    {"type": "text", "value": "<p>a</p>"},
                    {"type": "form", "value": 12},
                ],
            },
        }
        section = migration.block_to_section(block)
        self.assertEqual(section["references"], [])
        self.assertEqual(section["body"], "<p>a</p>")
