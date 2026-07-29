# gitignored

Inspect untracked and ignored paths inside a Git worktree, including ignored directories that often hide in plain sight.

## About

`gitignored` answers a common question: beyond normal `git status`, what is being left out of a repository, and where? It walks the tracked tree and nearby working tree, cross-references `.gitignore`, `.git/info/exclude`, and global excludes, and produces machine-readable reports for audits, cleanup, and repo hygiene workflows.

## Features

- List untracked files and directories
- Surface ignored paths with matched ignore source
- Include or exclude specific directories
- JSON and human-readable report output
- Stable exit codes for automation

## Installation

```bash
python -m pip install -e .
```

## Usage

```bash
gitignored
gitignored --repo /path/to/repo --json
gitignored --ignore-source --untracked
```

### Examples

Inspect the current repository:

```bash
gitignored
```

Inspect a different repository, show ignore sources:

```bash
gitignored --repo ../other-repo --ignore-source --json
```

Limit to untracked entries only:

```bash
gitignored --untracked
```

## Project structure

```
gitignored
├── README.md
├── pyproject.toml
├── gitignored
│   └── __init__.py
│   └── cli.py
│   └── collector.py
│   └── model.py
│   └── report.py
└── tests
    └── test_gitignored.py
```

## Tags / keywords

git, gitignore, repository audit, developer tool, cli, python
