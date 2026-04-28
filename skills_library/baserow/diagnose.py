from __future__ import annotations

import os
from pathlib import Path

from config import load_config


def _mask(value: str | None) -> str:
    if not value:
        return "<missing>"
    if len(value) <= 8:
        return "<set>"
    return f"{value[:4]}...{value[-4:]}"


def main() -> None:
    config = load_config()
    print("Baserow diagnostics")
    print(f"base_url={config.base_url}")
    print(f"default_account={config.default_account}")
    print(f"first_database_name={config.first_database_name!r}")
    for name, account in config.accounts.items():
        print(f"token_{name}={_mask(account.token)}")

    env_path = Path(__file__).resolve().parent / ".env"
    print(f"env_file_exists={env_path.exists()}")
    if env_path.exists():
        print(f"env_file={env_path}")
        print("env_file_preview=")
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.strip().startswith("#"):
                key = line.split("=", 1)[0].strip()
                print(f"  - {key}")


if __name__ == "__main__":
    main()
