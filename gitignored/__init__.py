"""gitignored."""

from gitignored.cli import main
from gitignored.collector import collect
from gitignored.model import Entry
from gitignored.report import format_json, format_text

__all__ = ["Entry", "collect", "format_json", "format_text", "main"]
