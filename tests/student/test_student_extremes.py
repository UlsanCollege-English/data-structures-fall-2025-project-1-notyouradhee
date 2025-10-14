import pytest

from scheduler import Scheduler


def test_create_negative_capacity_raises():
    s = Scheduler()
    with pytest.raises(ValueError):
        s.create_queue("Bad", -1)


def test_enqueue_unknown_queue_error():
    s = Scheduler()
    logs = s.enqueue("NoSuch", "latte")
    assert any("event=error" in l and "reason=unknown_queue" in l for l in logs)


def test_mark_skip_unknown_queue_error():
    s = Scheduler()
    logs = s.mark_skip("Nobody")
    assert any("event=error" in l and "reason=unknown_queue" in l for l in logs)


def test_zero_capacity_queue_rejects_all(capsys):
    s = Scheduler()
    s.create_queue("Z", 0)
    logs = s.enqueue("Z", "latte")
    out, _ = capsys.readouterr()
    assert "Sorry, we're at capacity." in out
    assert any("reason=full" in l for l in logs)


def test_run_no_queues_returns_empty():
    s = Scheduler()
    assert s.run(quantum=1, steps=None) == []


def test_circular_buffer_wrap_and_finish():
    s = Scheduler()
    s.create_queue("Q", 2)
    # enq two items that will require multiple cycles when quantum smaller
    s.enqueue("Q", "latte")
    s.enqueue("Q", "latte")

    logs = s.run(quantum=1, steps=None)

    # both tasks should eventually finish
    assert any("event=finish queue=Q task=Q-001" in l for l in logs)
    assert any("event=finish queue=Q task=Q-002" in l for l in logs)
