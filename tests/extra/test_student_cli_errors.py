import io
import sys

import pytest


def run_cli_with_input(input_str, capsys, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO(input_str))
    from cli import main
    main()
    out, _ = capsys.readouterr()
    return out


def test_cli_create_bad_args(monkeypatch, capsys):
    out = run_cli_with_input("CREATE only_one_arg\n\n", capsys, monkeypatch)
    assert "time=? event=error reason=bad_args" in out


def test_cli_enq_bad_args(monkeypatch, capsys):
    out = run_cli_with_input("ENQ only_one\n\n", capsys, monkeypatch)
    assert "time=? event=error reason=bad_args" in out


def test_cli_skip_bad_args(monkeypatch, capsys):
    out = run_cli_with_input("SKIP too many args extra\n\n", capsys, monkeypatch)
    assert "time=? event=error reason=bad_args" in out


def test_cli_run_bad_args_count(monkeypatch, capsys):
    out = run_cli_with_input("RUN\n\n", capsys, monkeypatch)
    assert "time=? event=error reason=bad_args" in out
    out = run_cli_with_input("RUN 1 2 3\n\n", capsys, monkeypatch)
    assert "time=? event=error reason=bad_args" in out


def test_cli_non_integer_values(monkeypatch, capsys):
    # non-integer capacity
    out = run_cli_with_input("CREATE Q not_an_int\n\n", capsys, monkeypatch)
    assert "time=? event=error reason=bad_args" in out

    # non-integer quantum
    out = run_cli_with_input("RUN not_int\n\n", capsys, monkeypatch)
    assert "time=? event=error reason=bad_args" in out


def test_cli_unknown_command(monkeypatch, capsys):
    out = run_cli_with_input("FLIP something\n\n", capsys, monkeypatch)
    assert "time=? event=error reason=unknown_command" in out
