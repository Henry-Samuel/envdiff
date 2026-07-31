# CfgDiff

Diff configuration files across common formats and report structural semantic changes.

## About

Many tools need to compare configuration rather than plain text. CfgDiff converts
JSON, YAML, TOML, and Ini files into structured declarations, then reports:
missing keys,
value changes,
and additions/removals.

## Features

- JSON, YAML, TOML, and Ini support.
- Structured key paths, e.g. `app.database.pool.max`.
- Value normalization for type-stable comparison.
- CLI and Python API.
- Zero external network requirements.

## Installation

```bash
python -m pip install .
```

Development install:

```bash
python -m pip install -e ".[dev]"
```

## Usage

CLI:

```bash
cfgdiff old.ini new.ini
cfgdiff app.prod.json app.staging.json
```

Exit codes:
- `0` - no differences
- `1` - differences found
- `2` - missing file or unsupported format

Python API:

```py
from pathlib import Path
from cfgdiff import diff_files

entries = diff_files(Path("old.yaml"), Path("new.yaml"))
for entry in entries:
    print(entry.render())
```

## Project structure

- `cfgdiff/` package.
- `tests/` pytest suite.
- `docs/` usage references.

## Tags / keywords

config, diff, json, yaml, toml, ini, cli, comparison
