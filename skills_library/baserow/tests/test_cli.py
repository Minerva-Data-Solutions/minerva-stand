from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
import json
import unittest

from cli import _dry_run, _ensure_confirmed


class CliTest(unittest.TestCase):
    def test_dry_run_output_is_deterministic(self):
        output = StringIO()
        with redirect_stdout(output):
            _dry_run("test", "delete-row", {"table_id": "1", "row_id": "2"}, ["confirm required"])

        payload = json.loads(output.getvalue())

        self.assertEqual(payload, {
            "account": "test",
            "dry_run": True,
            "error": None,
            "ok": True,
            "operation": "delete-row",
            "result": {"row_id": "2", "table_id": "1"},
            "status": 200,
            "warnings": ["confirm required"],
        })

    def test_delete_confirmation_guard_returns_dry_run(self):
        output = StringIO()
        with redirect_stdout(output):
            confirmed = _ensure_confirmed(
                Namespace(confirm=False),
                "test",
                "delete-row",
                {"table_id": "1", "row_id": "2"},
                "Pass --confirm to delete this row.",
            )

        payload = json.loads(output.getvalue())

        self.assertIs(confirmed, False)
        self.assertIs(payload["dry_run"], True)
        self.assertEqual(payload["result"], {"row_id": "2", "table_id": "1"})
