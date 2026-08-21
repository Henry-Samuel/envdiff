from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from badgepolice import AuditConfig, BadgeAuditReport, BadgeEntry, BadgeIssue, audit_markdown, main


def _report(text: str, config: AuditConfig | None = None) -> BadgeAuditReport:
    return audit_markdown(text, Path("README.md"), config=config)


def test_no_badges_returns_empty_report() -> None:
    assert _report("# Hello\n").issues == []


def test_discouraged_shields_io_domain_flagged() -> None:
    report = _report("![CI](https://img.shields.io/badge/ci-passing-blue)\n")
    assert report.issues == [
        BadgeIssue(1, "Badge domain is discouraged: img.shields.io.", BadgeEntry(1, "CI", "https://img.shields.io/badge/ci-passing-blue", "img.shields.io"))
    ]


def test_non_http_url_flagged() -> None:
    report = _report("![CI](ftp://example.com/badge.svg)\n")
    assert report.issues == [
        BadgeIssue(1, "Badge URL is not HTTP(S).", BadgeEntry(1, "CI", "ftp://example.com/badge.svg", "example.com"))
    ]


def test_multiple_badges_on_single_line() -> None:
    report = _report(
        "![A](https://img.shields.io/a) ![B](https://img.shields.io/b)\n"
    )
    assert len(report.issues) == 2
    assert [issue.badge.label for issue in report.issues] == ["A", "B"]


def test_custom_allowed_domain_suppresses_discouraged_domain() -> None:
    report = _report("![CI](https://img.shields.io/badge/ci-passing-blue)\n")
    assert len(report.issues) == 1

    report2 = _report("![CI](https://img.shields.io/badge/ci-passing-blue)\n", config=AuditConfig(discouraged_domains=()))
    assert report2.issues == []


def test_main_returns_zero_on_clean_path(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("# clean\n", encoding="utf-8")
    assert main([str(readme)]) == 0


def test_main_returns_nonzero_on_violation(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("![CI](https://img.shields.io/badge/ci-passing-blue)\n", encoding="utf-8")
    assert main([str(readme)]) == 1
