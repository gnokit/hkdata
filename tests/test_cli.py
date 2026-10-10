import argparse
import json

from hkdata import cli


def test_search_local_prints_kind_once(monkeypatch, capsys):
    # A log record's title already carries its "[kind]" prefix — the CLI must
    # not wrap it a second time.
    monkeypatch.setattr(cli, "search_local", lambda q, top_n=10: [
        ("negative", 1.0, {"title": "[negative] crime card",
                           "description": "x" * 200}),
    ])
    rc = cli.cmd_search_local(argparse.Namespace(keywords=["crime"], top_n=5))
    out = capsys.readouterr().out
    assert rc == 0
    assert "[negative] [negative]" not in out
    assert "[negative] crime card" in out


def test_info_returns_array_for_single_id(monkeypatch, capsys):
    monkeypatch.setattr(cli, "info_multiple",
                        lambda ids: [{"data": {"name": ids[0]}, "error": None}])
    rc = cli.cmd_info(argparse.Namespace(dataset_ids=["hk-x"]))
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert isinstance(payload, list)
    assert payload[0]["name"] == "hk-x"


def test_info_all_errors_exit_nonzero(monkeypatch, capsys):
    monkeypatch.setattr(cli, "info_multiple",
                        lambda ids: [{"data": None, "error": "boom"} for _ in ids])
    rc = cli.cmd_info(argparse.Namespace(dataset_ids=["a", "b"]))
    captured = capsys.readouterr()
    assert rc == 1
    assert "boom" in captured.err
