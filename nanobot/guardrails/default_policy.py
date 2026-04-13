from __future__ import annotations

from copy import deepcopy

_WORKSPACE_PATHS = ["${WORKSPACE}", "${MEDIA}"]
_BLOCKED_PATHS = [
    "/dev",
    "/proc",
    "/sys",
    "/etc",
    "/bin",
    "/sbin",
    "/usr",
    "/System",
    "/private",
    "~/.ssh",
    "~/.aws",
    "~/.config",
]

DEFAULT_GUARDRAILS_POLICY: dict[str, object] = {
    "tools": {
        "exec": {
            "allowed_commands": [],
            "blocked_commands": [
                "rm",
                "del",
                "rmdir",
                "shutdown",
                "reboot",
                "poweroff",
                "mkfs",
                "format",
                "dd",
                "diskpart",
            ],
            "allowed_paths": _WORKSPACE_PATHS,
            "blocked_paths": _BLOCKED_PATHS,
        },
        "read_file": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": _WORKSPACE_PATHS,
            "blocked_paths": _BLOCKED_PATHS,
        },
        "write_file": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": _WORKSPACE_PATHS,
            "blocked_paths": _BLOCKED_PATHS,
        },
        "edit_file": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": _WORKSPACE_PATHS,
            "blocked_paths": _BLOCKED_PATHS,
        },
        "list_dir": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": _WORKSPACE_PATHS,
            "blocked_paths": _BLOCKED_PATHS,
        },
        "glob": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": _WORKSPACE_PATHS,
            "blocked_paths": _BLOCKED_PATHS,
        },
        "grep": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": _WORKSPACE_PATHS,
            "blocked_paths": _BLOCKED_PATHS,
        },
        "notebook_edit": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": _WORKSPACE_PATHS,
            "blocked_paths": _BLOCKED_PATHS,
        },
        "web_search": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": [],
            "blocked_paths": [],
        },
        "web_fetch": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": [],
            "blocked_paths": [],
        },
        "message": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": [],
            "blocked_paths": [],
        },
        "spawn": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": [],
            "blocked_paths": [],
        },
        "cron": {
            "allowed_commands": [],
            "blocked_commands": [],
            "allowed_paths": [],
            "blocked_paths": [],
        },
    }
}


def build_default_policy() -> dict[str, object]:
    return deepcopy(DEFAULT_GUARDRAILS_POLICY)
