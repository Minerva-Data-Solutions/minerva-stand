from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class BaserowAccount:
    name: str
    token: str


@dataclass(frozen=True)
class BaserowConfig:
    base_url: str
    accounts: dict[str, BaserowAccount]
    default_account: str
    first_database_name: str | None = None
    jwt_access_token: str = ""
    jwt_refresh_token: str = ""


def _load_dotenv_file(path: str = ".env") -> None:
    env_path = Path(__file__).resolve().parent / path
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_config() -> BaserowConfig:
    _load_dotenv_file()
    base_url = os.getenv("BASEROW_BASE_URL", "https://api.baserow.io")
    accounts = {
        "trendia": BaserowAccount("trendia", os.getenv("BASEROW_TOKEN_TRENDIA", "").strip()),
        "bah_studios": BaserowAccount("bah_studios", os.getenv("BASEROW_TOKEN_BAH_STUDIOS", "").strip()),
        "minerva": BaserowAccount("minerva", os.getenv("BASEROW_TOKEN_MINERVA", "").strip()),
    }
    default_account = os.getenv("BASEROW_DEFAULT_ACCOUNT", "bah_studios").strip()
    first_database_name = os.getenv("BASEROW_FIRST_DATABASE_NAME")
    return BaserowConfig(
        base_url=base_url,
        accounts=accounts,
        default_account=default_account,
        first_database_name=first_database_name,
        jwt_access_token=os.getenv("BASEROW_JWT_ACCESS_TOKEN", "").strip(),
        jwt_refresh_token=os.getenv("BASEROW_JWT_REFRESH_TOKEN", "").strip(),
    )
