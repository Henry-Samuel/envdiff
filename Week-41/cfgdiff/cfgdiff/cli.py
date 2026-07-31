from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cfgdiff.diff import DiffEntry, diff_files


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="cfgdiff", description="Diff config files.")
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args.left.exists():
        print(f"cfgdiff: missing file: {args.left}", file=sys.stderr)
        return 2
    if not args.right.exists():
        print(f"cfgdiff: missing file: {args.right}", file=sys.stderr)
        return 2
    entries = diff_files(args.left, args.right)
    for entry in entries:
        print(entry.render())
    return min(len(entries), 255)
