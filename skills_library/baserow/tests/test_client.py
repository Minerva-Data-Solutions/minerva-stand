import unittest

from config import BaserowAccount, BaserowConfig
from baserow_client import BaserowClient


def make_config():
    return BaserowConfig(
        base_url="https://api.baserow.io",
        accounts={"test": BaserowAccount("test", "database-token")},
        default_account="test",
        jwt_access_token="jwt-access",
        jwt_refresh_token="jwt-refresh",
    )


class ClientTest(unittest.TestCase):
    def test_database_token_header_is_explicit_token_auth(self):
        client = BaserowClient(make_config())

        headers = client._headers("Token", "database-token", json_body=True)

        self.assertEqual(headers, {
            "Authorization": "Token database-token",
            "Content-Type": "application/json",
        })

    def test_jwt_header_is_explicit_jwt_auth(self):
        client = BaserowClient(make_config())

        headers = client._headers("JWT", "jwt-access", json_body=False)

        self.assertEqual(headers, {"Authorization": "JWT jwt-access"})

    def test_schema_request_is_unavailable_for_now(self):
        client = BaserowClient(make_config())

        result = client.create_table(1, {"name": "Blocked"})

        self.assertEqual(result.status, 501)
        self.assertEqual(result.json()["error"], "SCHEMA_OPERATIONS_UNAVAILABLE")
