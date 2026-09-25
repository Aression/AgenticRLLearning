#!/usr/bin/env python3
"""Global kill switch for model calls.

Every script that talks to a model provider must call ``require_llm_enabled`` before
its first request. The switch lives in ``harness.config.json``::

    "llm": { "enabled": false, "disabledReason": "..." }

While it is off, ``cards.py run/deepen`` and ``agent_audit.py`` exit immediately with
code 3 and spend no tokens. Offline commands (``cards.py check/status/fetch``,
``harness.py check``, ``atlas_db.py``) keep working, so a paused repository can still
be validated and inspected.

Set ``ATLAS_LLM_ENABLED=1`` to override the file for a single invocation.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "harness.config.json"
ENV_OVERRIDE = "ATLAS_LLM_ENABLED"
PAUSED_EXIT_CODE = 3


def llm_policy() -> dict[str, Any]:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    policy = config.get("llm") if isinstance(config, dict) else None
    return policy if isinstance(policy, dict) else {}


def llm_enabled(policy: dict[str, Any] | None = None) -> bool:
    override = os.environ.get(ENV_OVERRIDE)
    if override is not None and override.strip():
        return override.strip().lower() in {"1", "true", "yes", "on"}
    return bool((policy if policy is not None else llm_policy()).get("enabled", True))


def require_llm_enabled(script: str) -> None:
    """Exit with ``PAUSED_EXIT_CODE`` when the repository has model calls paused."""
    policy = llm_policy()
    if llm_enabled(policy):
        return
    reason = str(policy.get("disabledReason") or "no reason recorded")
    print(f"{script}: LLM calls are paused (harness.config.json → llm.enabled=false).", file=sys.stderr)
    print(f"{script}: reason: {reason}", file=sys.stderr)
    print(f"{script}: resume by setting llm.enabled=true or {ENV_OVERRIDE}=1.", file=sys.stderr)
    raise SystemExit(PAUSED_EXIT_CODE)
