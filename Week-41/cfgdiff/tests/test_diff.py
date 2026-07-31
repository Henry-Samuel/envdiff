from pathlib import Path

from cfgdiff.diff import DiffEntry, diff_files, load_config, normalize_value


def test_normalize_value_preserves_scalar_types():
    assert normalize_value(True) is True
    assert normalize_value(False) is False
    assert normalize_value(10) == "10"
    assert normalize_value(3.5) == "3.5"
    assert normalize_value(None) is None
    assert normalize_value("alpha") == "alpha"


def test_normalize_value_collapses_collections():
    assert normalize_value([1, 2]) == "[1, 2]"
    assert normalize_value([True, False]) == "[True, False]"


def test_load_json(tmp_path: Path):
    p = tmp_path / "sample.json"
    p.write_text('{"app":{"port":8080,"host":"127.0.0.1"}}')
    cfg = load_config(p)
    assert cfg["app"]["port"] == 8080


def test_load_ini(tmp_path: Path):
    p = tmp_path / "sample.ini"
    p.write_text("[settings]\nport = 80\n")
    cfg = load_config(p)
    assert cfg["settings"]["port"] == "80"


def test_diff_files_positive(tmp_path: Path):
    left = tmp_path / "a.json"
    right = tmp_path / "b.json"
    left.write_text('{"app":{"port":80,"host":"0.0.0.0"}}')
    right.write_text('{"app":{"port":8080,"host":"0.0.0.0"}}')
    entries = diff_files(left, right)
    assert len(entries) == 1
    assert entries[0].path == ("app", "port")
    assert entries[0].message == "value changed: 80 -> 8080"


def test_diff_files_negative(tmp_path: Path):
    left = tmp_path / "a.json"
    right = tmp_path / "b.json"
    left.write_text('{"app":{"port":80,"host":"0.0.0.0"}}')
    right.write_text('{"app":{"port":80,"host":"0.0.0.0"}}')
    entries = diff_files(left, right)
    assert entries == ()


def test_diff_files_missing_and_added(tmp_path: Path):
    left = tmp_path / "a.json"
    right = tmp_path / "b.json"
    left.write_text('{"app":{"port":80}}')
    right.write_text('{"app":{"port":80,"host":"0.0.0.0"}}')
    entries = diff_files(left, right)
    assert [e.render() for e in entries] == ["app.host: missing on left"]
    assert len(entries) == 1
