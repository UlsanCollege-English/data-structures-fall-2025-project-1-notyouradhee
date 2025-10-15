import io
import sys

from scheduler import Scheduler


def test_parser_blank_and_comment():
    from parser import parse_command

    # blank line -> None
    assert parse_command("   \n") is None
    # comment line -> None
    assert parse_command("# this is a comment") is None
    # normal command parsing and uppercasing
    cmd, args = parse_command("enq Mobile latte")
    assert cmd == "ENQ"
    assert args == ["Mobile", "latte"]


def test_cli_integration_prints_display_and_break(monkeypatch, capsys):
    # Prepare an input stream that creates a queue, enqueues, runs, then ends session
    input_data = """CREATE Mobile 2
ENQ Mobile latte
RUN 1

"""
    monkeypatch.setattr(sys, "stdin", io.StringIO(input_data))

    # Run the CLI main function
    from cli import main
    main()

    out, _ = capsys.readouterr()
    # Check create/enqueue logs
    assert "event=create queue=Mobile" in out
    assert "event=enqueue queue=Mobile task=Mobile-001" in out
    # Display snapshot should appear after RUN turn
    assert "display time=" in out
    # Blank line should end the session
    assert "Break time!" in out


def test_enqueue_unknown_item_and_capacity_message(capsys):
    s = Scheduler()
    s.create_queue("WalkIns", 1)

    # Unknown item
    logs = s.enqueue("WalkIns", "unknown_drink")
    out, _ = capsys.readouterr()
    assert "Sorry, we don't serve that." in out
    assert any("event=reject" in l and "reason=unknown_item" in l for l in logs)

    # Fill capacity
    s.enqueue("WalkIns", "latte")
    # Next enqueue should reject and print capacity message
    logs = s.enqueue("WalkIns", "tea")
    out, _ = capsys.readouterr()
    assert "Sorry, we're at capacity." in out
    assert any("event=reject" in l and "reason=full" in l for l in logs)


def test_skip_consumed_and_no_time_advance():
    s = Scheduler()
    s.create_queue("Q", 2)
    s.enqueue("Q", "tea")  # 1 minute

    # Mark skip and run one turn: skip should consume flag and no work occurs
    s.mark_skip("Q")
    logs = s.run(quantum=1, steps=1)

    # There should be a run event, but no work/finish for the skipped turn
    assert any("event=run queue=Q" in l for l in logs)
    assert not any("event=work" in l or "event=finish" in l for l in logs)
