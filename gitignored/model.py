from __future__ import annotations

__all__ = ["Entry", "collect"]


class Entry:
    __slots__ = ("path", "kind", "ignore_source")

    def __init__(self, path: str, kind: str, ignore_source: str | None = None) -> None:
        self.path = path
        self.kind = kind
        self.ignore_source = ignore_source

    def as_dict(self) -> dict:
        data = {"path": self.path, "kind": self.kind}
        if self.ignore_source is not None:
            data["ignore_source"] = self.ignore_source
        return data


