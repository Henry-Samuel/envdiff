from __future__ import annotations

import os
import subprocess
from typing import Iterable, Iterator

from .model import Entry


def _git(args: list[str], repo: str) -> str:
    result = subprocess.run(
        ["git"] + args,
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout


def _parse_status(repo: str) -> tuple[list[str], list[str]]:
    ignored: list[str] = []
    untracked: list[str] = []
    for line in _git(["status", "--ignored=traditional", "--short", "--untracked-files=all"], repo).splitlines():
        if not line.strip("\n"):
            continue
        state = line[:2]
        path = line[3:]
        if state in {"!!", "I"} or (state[0] in {"!", "I"} or state[1] in {"!", "I"}):
            ignored.append(path)
        elif state == "??":
            untracked.append(path)
    return ignored, untracked


def _ignored_source(path: str, repo: str) -> str | None:
    source = _git(["check-ignore", "-v", "--", path], repo).strip()
    return source or None


def _normalize(paths: Iterable[str], repo: str) -> list[str]:
    repo = repo.rstrip("/")
    normalized: list[str] = []
    for raw in paths:
        raw = raw.strip()
        if not raw:
            continue
        if os.path.isdir(os.path.join(repo, raw)) and not raw.endswith(os.sep):
            raw = raw.rstrip("/") + "/"
        normalized.append(raw)
    return normalized


def collect(
    repo: str,
    show_ignore_source: bool = False,
    untracked_only: bool = False,
    excluded_dirs: Iterable[str] | None = None,
) -> tuple[list[Entry], list[Entry]]:
    repo = os.path.abspath(repo)
    ignored_raw, untracked_raw = _parse_status(repo)
    ignored_norm = _normalize(ignored_raw, repo)
    untracked_norm = _normalize(untracked_raw, repo)

    prefix = repo + os.sep
    excluded_dirs = [d.rstrip("/") for d in (excluded_dirs or [])]

    def _excluded(path: str) -> bool:
        for directory in excluded_dirs:
            if path == directory or path.startswith(directory.rstrip("/") + "/"):
                return True
        return False

    entries: list[Entry] = []

    if not untracked_only:
        for path in ignored_norm:
            if _excluded(path):
                continue
            source = _ignored_source(path, repo) if show_ignore_source else None
            entries.append(Entry(path, "ignored", source))

    for path in untracked_norm:
        if _excluded(path):
            continue
        entries.append(Entry(path, "untracked"))

    ignored_entries = [entry for entry in entries if entry.kind == "ignored"]
    untracked_entries = [entry for entry in entries if entry.kind == "untracked"]
    return ignored_entries, untracked_entries
