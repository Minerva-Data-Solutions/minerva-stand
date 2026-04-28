import unittest

from schema_manifest import plan_schema


class SchemaManifestTest(unittest.TestCase):
    def test_plan_schema_creates_missing_table_with_fields(self):
        live = {"account": "test", "database_id": 1, "tables": []}
        desired = {
            "database_id": 1,
            "tables": [
                {
                    "name": "Companies",
                    "fields": [
                        {"name": "Name", "type": "text"},
                    ],
                }
            ],
        }

        plan = plan_schema(live, desired)

        self.assertEqual(plan["action_count"], 1)
        self.assertEqual(plan["actions"][0], {
            "action": "create_table",
            "database_id": 1,
            "fields": [{"name": "Name", "type": "text"}],
            "payload": {"name": "Companies"},
            "requires_confirm": False,
        })

    def test_plan_schema_marks_field_type_change_as_confirm_required(self):
        live = {
            "account": "test",
            "database_id": 1,
            "tables": [
                {
                    "id": 10,
                    "name": "Companies",
                    "fields": [
                        {"id": 20, "name": "Status", "type": "text", "primary": False},
                    ],
                }
            ],
        }
        desired = {
            "database_id": 1,
            "tables": [
                {
                    "name": "Companies",
                    "fields": [
                        {"name": "Status", "type": "single_select"},
                    ],
                }
            ],
        }

        plan = plan_schema(live, desired)

        self.assertIs(plan["requires_confirm"], True)
        self.assertEqual(plan["actions"], [
            {
                "action": "update_field",
                "field_id": 20,
                "payload": {"type": "single_select"},
                "requires_confirm": True,
            }
        ])

    def test_plan_schema_delete_missing_field_skips_primary_field(self):
        live = {
            "account": "test",
            "database_id": 1,
            "tables": [
                {
                    "id": 10,
                    "name": "Companies",
                    "fields": [
                        {"id": 20, "name": "Name", "type": "text", "primary": True},
                        {"id": 21, "name": "Old", "type": "text", "primary": False},
                    ],
                }
            ],
        }
        desired = {
            "database_id": 1,
            "tables": [
                {
                    "name": "Companies",
                    "delete_missing_fields": True,
                    "fields": [
                        {"name": "Name", "type": "text"},
                    ],
                }
            ],
        }

        plan = plan_schema(live, desired)

        self.assertEqual(plan["actions"], [
            {
                "action": "delete_field",
                "field_id": 21,
                "requires_confirm": True,
            }
        ])
