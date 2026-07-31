import subprocess
import sys
from pathlib import Path

from cfgdiff.cli import main


def test_cli_missing_left(tmp_path: Path):
    rc = main([str(tmp_path / "missing.ini"), str(tmp_path / "other.ini")])
    assert rc == 2


def test_cli_equal_files(tmp_path: Path):
    left = tmp_path / "a.json"
    right = tmp_path / "b.json"
    left.write_text('{"app":{"port":80}}')
    right.write_text('{"app":{"port":80}}')
    rc = main([str(left), str(right)])
    assert rc == 0


def test_cli_output_diff(tmp_path: Path):
    left = tmp_path / "a.json"
    right = tmp_path / "b.json"
    left.write_text('{"app":{"port":80}}')
    right.write_text('{"app":{"port":8080}}')
    rc = main([str(left), str(right)])
    assert rc == 1
