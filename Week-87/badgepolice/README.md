# badgepolice

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Audit README badge hygiene for open-source projects. `badgepolice` scans Markdown badges and reports discouraged Shields.io domains, deprecated prefixes, and non-HTTP(S) URLs.

## About

Badges clutter READMEs fast, and some badge URLs rot into deprecated or problematic patterns. `badgepolice` automates the scan so maintainers can clean them up before they accumulate.

## Features

- Scan single README files or entire directories recursively.
- Detect discouraged badge domains, including Shields.io hostnames.
- Detect deprecated Shields.io prefixes, such as VersionEye endpoints.
- Flag badges with non-HTTP(S) URL schemes.
- JSON output for automation/CI.
- Configurable allowlists and toggleable rule groups.

## Installation

```bash
python -m pip install badgepolice
```

## Usage

```bash
badgepolice README.md
badgepolice docs/ README.md
badgepolice --format json .
badgepolice --allow-domain shields.io README.md
```

## Project structure

```
badgepolice/
  README.md
  badgepolice.py
  pyproject.toml
  tests/
    test_badgepolice.py
```

## Tags

badge, readme, lint, shields, markdown, ci
