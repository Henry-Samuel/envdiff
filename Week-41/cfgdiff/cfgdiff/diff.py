from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple


@dataclass(frozen=True)
class DiffEntry:
    path: Tuple[str, ...]
    message: str

    def label(self) -> str:
        return ".".join(self.path) if self.path else "(root)"

    def render(self) -> str:
        return f"{self.label()}: {self.message}"


def _decode_section_key(raw: str) -> Tuple[str, str]:
    head, sep, tail = raw.partition("::")
    return (head.strip() or "DEFAULT", tail.strip())


def _strip_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith(";"):
            continue
        out.append(line)
    return "\n".join(out)


def load_config(path: Path) -> Mapping[str, Any]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        import json

        return json.loads(text)
    if suffix in {".yaml", ".yml"}:
        import yaml

        return yaml.safe_load(text) or {}
    if suffix == ".toml":
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore
        return tomllib.loads(text)
    if suffix in {".ini", ".cfg"}:
        import configparser

        text = _strip_comments(text)
        cp = configparser.ConfigParser()
        cp.read_string(text)
        return {section: dict(cp[section]) for section in cp.sections()}
    raise ValueError(f"unsupported config format: {suffix}")


def _flatten_mapping(
    mapping: Mapping[str, Any], prefix: Tuple[str, ...] = ()
) -> Dict[Tuple[str, ...], Any]:
    out: Dict[Tuple[str, ...], Any] = {}
    for key, value in mapping.items():
        path = prefix + (str(key),)
        if isinstance(value, Mapping):
            out.update(_flatten_mapping(value, prefix=path))
        else:
            out[path] = value
    return out


def normalize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(str(normalize_value(item)) for item in value) + "]"
    return str(value)


def diff_files(left_path: Path, right_path: Path) -> Tuple[DiffEntry, ...]:
    left = _flatten_mapping(load_config(left_path))
    right = _flatten_mapping(load_config(right_path))
    all_keys = sorted(left.keys() | right.keys())
    entries: list[DiffEntry] = []
    for key in all_keys:
        if key not in left:
            entries.append(DiffEntry(path=key, message="missing on left"))
        elif key not in right:
            entries.append(DiffEntry(path=key, message="missing on right"))
        else:
            lv = normalize_value(left[key])
            rv = normalize_value(right[key])
            if lv != rv:
                entries.append(
                    DiffEntry(
                        path=key,
                        message=f"value changed: {lv} -> {rv}",
                    )
                )
    return tuple(entries)
