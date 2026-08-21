from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence

__version__ = "0.1.0"

BADGE_RE = re.compile(r"!\[(?P<label>[^\]]*)\]\((?P<url>[^)]+)\)")
HTTP_RE = re.compile(r"^https?://", re.IGNORECASE)
SHIELDS_IO_RE = re.compile(r"https?://img\.shields\.io", re.IGNORECASE)

DEFAULT_DISCOURAGED_DOMAINS: tuple[str, ...] = ("img.shields.io",)
DEFAULT_DEPRECATED_PREFIXES: tuple[str, ...] = ("https://www.versioneye.com/",)


@dataclass(frozen=True)
class BadgeEntry:
    line: int
    label: str
    url: str
    domain: str


@dataclass
class BadgeIssue:
    line: int
    message: str
    badge: BadgeEntry


@dataclass
class BadgeAuditReport:
    file: Path
    issues: List[BadgeIssue] = field(default_factory=list)

    def as_rows(self) -> List[dict[str, object]]:
        return [
            {
                "file": str(self.file),
                "line": issue.line,
                "message": issue.message,
                "badge_label": issue.badge.label,
                "badge_url": issue.badge.url,
            }
            for issue in self.issues
        ]


def _domain_from_url(url: str) -> str:
    cleaned = url.split("?", 1)[0].split("#", 1)[0]
    if "://" in cleaned:
        cleaned = cleaned.split("://", 1)[1]
    cleaned = cleaned.split("/", 1)[0]
    return cleaned.lower()


def _audit_badge(badge: BadgeEntry, config: AuditConfig) -> List[BadgeIssue]:
    issues: List[BadgeIssue] = []
    if not HTTP_RE.match(badge.url):
        issues.append(BadgeIssue(badge.line, "Badge URL is not HTTP(S).", badge))
    if SHIELDS_IO_RE.match(badge.url):
        if config.flag_deprecated_shields_io and any(
            badge.url.startswith(prefix) for prefix in config.deprecated_prefixes
        ):
            issues.append(
                BadgeIssue(badge.line, "Shields.io URL matches a deprecated prefix.", badge)
            )
        domain = _domain_from_url(badge.url)
        if domain in config.discouraged_domains and config.flag_discouraged_domains:
            issues.append(
                BadgeIssue(badge.line, f"Badge domain is discouraged: {domain}.", badge)
            )
    return issues


@dataclass
class AuditConfig:
    discouraged_domains: Sequence[str] = DEFAULT_DISCOURAGED_DOMAINS
    deprecated_prefixes: Sequence[str] = DEFAULT_DEPRECATED_PREFIXES
    flag_discouraged_domains: bool = True
    flag_deprecated_shields_io: bool = True


def _scan_line(line: str, lineno: int) -> tuple[BadgeEntry, ...]:
    badges: List[BadgeEntry] = []
    for match in BADGE_RE.finditer(line):
        url = match.group("url").strip()
        badges.append(
            BadgeEntry(
                line=lineno,
                label=match.group("label"),
                url=url,
                domain=_domain_from_url(url),
            )
        )
    return tuple(badges)


def audit_markdown(text: str, path: Path, config: Optional[AuditConfig] = None) -> BadgeAuditReport:
    cfg = config or AuditConfig()
    report = BadgeAuditReport(file=path)
    for lineno, line in enumerate(text.splitlines(), start=1):
        for badge in _scan_line(line, lineno):
            report.issues.extend(_audit_badge(badge, cfg))
    return report


def audit_files(paths: Sequence[Path], config: Optional[AuditConfig] = None) -> List[BadgeAuditReport]:
    reports: List[BadgeAuditReport] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for file in sorted(path.rglob("README.md")):
                report = audit_markdown(file.read_text(encoding="utf-8"), file, config)
                if report.issues:
                    reports.append(report)
            continue
        report = audit_markdown(path.read_text(encoding="utf-8"), path, config)
        if report.issues:
            reports.append(report)
    return reports


def _render_rows(reports: Sequence[BadgeAuditReport], fmt: str) -> str:
    rows: List[dict[str, object]] = []
    for report in reports:
        rows.extend(report.as_rows())
    if not rows:
        return ""

    if fmt == "json":
        import json

        return json.dumps(rows, indent=2)

    return "\n".join(
        f"{r['file']}:{r['line']}: {r['message']} [{r['badge_label']}] {r['badge_url']}"
        for r in rows
    )


def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="badgepolice", description="Audit README badges.")
    parser.add_argument("paths", nargs="+", help="README files or directories to audit.")
    parser.add_argument(
        "--format",
        choices=("plain", "json"),
        default="plain",
        help="Output format.",
    )
    parser.add_argument(
        "--allow-domain",
        action="append",
        default=[],
        help="Allow a badge domain.",
    )
    parser.add_argument(
        "--no-discouraged-domains",
        action="store_true",
        help="Disable discouraged-domain checks.",
    )
    parser.add_argument(
        "--no-deprecated-shields-io",
        action="store_true",
        help="Disable deprecated Shields.io checks.",
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit.")
    args = parser.parse_args(argv)

    if args.version:
        print(f"badgepolice {__version__}")
        return 0

    discouraged = list(DEFAULT_DISCOURAGED_DOMAINS)
    for domain in args.allow_domain:
        if domain in discouraged:
            discouraged.remove(domain)

    config = AuditConfig(
        discouraged_domains=tuple(discouraged),
        flag_discouraged_domains=not args.no_discouraged_domains,
        flag_deprecated_shields_io=not args.no_deprecated_shields_io,
    )

    reports = audit_files(args.paths, config)
    output = _render_rows(reports, args.format)
    if output:
        print(output)
        return 1
    return 0


__all__ = [
    "BadgeAuditReport",
    "BadgeEntry",
    "BadgeIssue",
    "AuditConfig",
    "audit_markdown",
    "audit_files",
    "main",
]
