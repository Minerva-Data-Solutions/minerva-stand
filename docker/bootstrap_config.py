#!/usr/bin/env python3
"""Merge LLM API keys from the environment into ~/.nanobot/config.json.

Writes placeholder values like ${OPENROUTER_API_KEY} so nanobot's
resolve_config_env_vars() resolves them at runtime from the container environment
(including variables loaded from Docker Compose env_file).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> int:
    if os.environ.get("NANOBOT_SKIP_CONFIG_BOOTSTRAP"):
        return 0

    home = Path(os.environ.get("HOME", "/home/nanobot"))
    cfg_path = home / ".nanobot" / "config.json"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    if cfg_path.exists():
        try:
            with open(cfg_path, encoding="utf-8") as f:
                data: dict = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"bootstrap_config: cannot read {cfg_path}: {e}", file=sys.stderr)
            return 1
    else:
        from nanobot.config.schema import Config

        data = Config().model_dump(mode="json", by_alias=True)

    providers = data.setdefault("providers", {})

    provider_env_keys: list[tuple[str, str]] = [
        ("OPENROUTER_API_KEY", "openrouter"),
        ("ANTHROPIC_API_KEY", "anthropic"),
        ("OPENAI_API_KEY", "openai"),
        ("DEEPSEEK_API_KEY", "deepseek"),
        ("GROQ_API_KEY", "groq"),
        ("GEMINI_API_KEY", "gemini"),
        ("MISTRAL_API_KEY", "mistral"),
    ]

    changed = False
    for env_name, prov_name in provider_env_keys:
        if not os.environ.get(env_name):
            continue
        prov = providers.setdefault(prov_name, {})
        placeholder = f"${{{env_name}}}"
        current = prov.get("apiKey") or ""
        if current and not current.startswith("${"):
            continue
        if current != placeholder:
            prov["apiKey"] = placeholder
            changed = True

    agents = data.setdefault("agents", {})
    defaults = agents.setdefault("defaults", {})

    model = os.environ.get("NANOBOT_MODEL")
    if model and defaults.get("model") != model:
        defaults["model"] = model
        changed = True

    provider = os.environ.get("NANOBOT_PROVIDER")
    if provider and defaults.get("provider") != provider:
        defaults["provider"] = provider
        changed = True

    if not changed:
        return 0

    try:
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except OSError as e:
        print(f"bootstrap_config: cannot write {cfg_path}: {e}", file=sys.stderr)
        return 1

    print(f"bootstrap_config: updated {cfg_path} (API key placeholders from environment)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
