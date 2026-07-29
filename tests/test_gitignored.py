from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from gitignored.cli import main
from gitignored.collector import collect
from gitignored.model import Entry
from gitignored.report import format_json, format_text


def _prepare_repo() -> Path:
    repo = Path(tempfile.mkdtemp(prefix="gitignored-repo-"))
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "CI Bot"], cwd=repo, check=True, capture_output=True)
    (repo / "README.md").write_text("# hello\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    (repo / ".gitignore").write_text("build.log\napp.log\nsecret.txt\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "add ignore"], cwd=repo, check=True, capture_output=True)
    (repo / "build.log").write_text("build\n", encoding="utf-8")
    (repo / "app.log").write_text("app\n", encoding="utf-8")
    (repo / "secret.txt").write_text("secret\n", encoding="utf-8")
    (repo / "new.py").write_text("print(1)\n", encoding="utf-8")
    return repo


def test_main_missing_repo_exits_nonzero(capsys: pytest.CaptureFixture[str]) -> None:
    repo = Path(tempfile.mkdtemp(prefix="gitignored-bad-"))
    rc = main(["--repo", str(repo)])
    assert rc != 0
    captured = capsys.readouterr()
    assert "not a git repository" in captured.err


def test_main_clean_repo_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    repo = Path(tempfile.mkdtemp(prefix="gitignored-clean-"))
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "CI Bot"], cwd=repo, check=True, capture_output=True)
    (repo / "README.md").write_text("# hello\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    rc = main(["--repo", str(repo)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "ignored: 0" in captured.out
    assert "untracked: 0" in captured.out


def test_text_report_format() -> None:
    entries = [Entry("secret.txt", "ignored", ".gitignore:1:secret.txt"), Entry("draft.md", "untracked")]
    text = format_text(entries)
    assert text.startswith("ignored: 1\nuntracked: 1")
    assert ".gitignore:1:secret.txt" in text
    assert "draft.md" in text


def test_json_report_shape() -> None:
    entries = [Entry("secret.txt", "ignored", ".gitignore:1:secret.txt"), Entry("draft.md", "untracked")]
    payload = json.loads(format_json(entries))
    assert payload["counts"] == {"ignored": 1, "untracked": 1}
    assert len(payload["entries"]) == 2
    assert payload["entries"][0]["kind"] == "ignored"
    assert payload["entries"][1]["path"] == "draft.md"


def test_exclude_directory_removes_entries() -> None:
    repo = _prepare_repo()
    ignored, untracked = collect(str(repo), excluded_dirs=["docs/"])
    assert all(not entry.path.startswith("docs/") for entry in ignored + untracked)


def test_report_empty_collection() -> None:
    assert "ignored: 0" in format_text([])
    assert "untracked: 0" in format_text([])
    payload = json.loads(format_json([]))
    assert payload == {"counts": {"ignored": 0, "untracked": 0}, "entries": []}
