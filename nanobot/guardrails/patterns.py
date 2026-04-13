from __future__ import annotations

import re

DANGEROUS_COMMAND_NAMES = frozenset(
    {
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
        "sudo",
    }
)

DANGEROUS_SHELL_PATTERNS = (
    re.compile(r"\bcurl\b[^|]*\|\s*(?:bash|sh)\b", re.IGNORECASE),
    re.compile(r"\bwget\b[^|]*\|\s*(?:bash|sh)\b", re.IGNORECASE),
    re.compile(r">\s*/dev/(?:sd|disk|nvme)", re.IGNORECASE),
    re.compile(r"\bchmod\s+777\b", re.IGNORECASE),
    re.compile(r"\bchown\s+root\b", re.IGNORECASE),
    re.compile(r":\(\)\s*\{.*\};\s*:", re.IGNORECASE),
)

PROMPT_INJECTION_PATTERNS = (
    re.compile(r"\bignore (?:all |any |the )?(?:previous|prior|earlier) instructions\b", re.IGNORECASE),
    re.compile(r"\bignore (?:your|the) (?:system|developer) prompt\b", re.IGNORECASE),
    re.compile(r"\breveal (?:the )?(?:system|developer) prompt\b", re.IGNORECASE),
    re.compile(r"\bbypass (?:the )?(?:guardrails|safety|security)\b", re.IGNORECASE),
    re.compile(r"\bdisable (?:the )?(?:guardrails|safety|security)\b", re.IGNORECASE),
    re.compile(r"\boverride (?:the )?(?:policy|instructions|guardrails)\b", re.IGNORECASE),
)
