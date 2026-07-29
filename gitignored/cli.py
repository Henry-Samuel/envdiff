from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

from .collector import collect
from .report import format_json, format_text


def _positive_collect(args: argparse.Namespace) -> int:
    repo = args.repo
    ignored, untracked = collect(
        repo=repo,
        show_ignore_source=args.ignore_source,
        untracked_only=args.untracked,
        excluded_dirs=args.exclude,
    )
    entries = ignored + untracked
    if args.json:
        sys.stdout.write(format_json(entries))
    else:
        sys.stdout.write(format_text(entries) + "\n")

    if entries:
        return 1
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitignored",
        description="Inspect untracked and ignored paths inside a Git worktree.",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the repository to inspect.",
    )
    parser.add_argument(
        "--ignore-source",
        action="store_true",
        help="Report the ignore source matched for ignored paths.",
    )
    parser.add_argument(
        "--untracked",
        action="store_true",
        help="Report untracked files only.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude a directory path from results. May be repeated.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable text.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    repo = os.path.abspath(args.repo)
    git_dir = os.path.join(repo, ".git")
    if not os.path.isdir(git_dir):
        sys.stderr.write(f"error: not a git repository: {repo}\n")
        return 2

    return _positive_collect(args)


if __name__ == "__main__":
    raise SystemExit(main())
