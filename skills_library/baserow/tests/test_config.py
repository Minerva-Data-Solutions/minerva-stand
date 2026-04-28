import os
import unittest
from unittest.mock import patch

from config import load_config


class ConfigTest(unittest.TestCase):
    def test_load_config_has_three_accounts(self):
        config = load_config()
        self.assertEqual(set(config.accounts.keys()), {"trendia", "bah_studios", "minerva"})

    def test_load_config_reads_jwt_tokens(self):
        with patch.dict(os.environ, {"BASEROW_JWT_ACCESS_TOKEN": "access", "BASEROW_JWT_REFRESH_TOKEN": "refresh"}):
            config = load_config()

        self.assertEqual(config.jwt_access_token, "access")
        self.assertEqual(config.jwt_refresh_token, "refresh")
