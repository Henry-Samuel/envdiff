from __future__ import annotations

import json
from typing import Sequence

from .model import Entry


def format_text(entries: Sequence[Entry]) -> str:
    ignored = [entry for entry in entries if entry.kind == "ignored"]
    untracked = [entry for entry in entries if entry.kind == "untracked"]

    lines: list[str] = []
    lines.append(f"ignored: {len(ignored)}")
    lines.append(f"untracked: {len(untracked)}")
    lines.append("")

    for entry in ignored:
        suffix = f" <- {entry.ignore_source}" if entry.ignore_source else ""
        lines.append(f"ignored: {entry.path}{suffix}")

    for entry in untracked:
        lines.append(f"untracked: {entry.path}")

    return "\n".join(lines)


def format_json(entries: Sequence[Entry]) -> str:
    payload = {
        "counts": {
            "ignored": sum(1 for entry in entries if entry.kind == "ignored"),
            "untracked": sum(1 for entry in entries if entry.kind == "untracked"),
        },
        "entries": [entry.as_dict() for entry in entries],
    }
    return json.dumps(payload, indent=2) + "\n"
