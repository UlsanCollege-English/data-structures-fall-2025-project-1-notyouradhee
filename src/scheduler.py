"""
Scheduler + QueueRR stubs for the Multi-Queue Round-Robin Café project.

Rules snapshot:
- Interactive program; blank line ends session with "Break time!".
- ENQ auto-generates task IDs as <queue_id>-NNN (1-based, zero-padded).
- Hardcoded menu must include at least these items (case-sensitive, lowercase):
    americano=2, latte=3, cappuccino=3, mocha=4, tea=1, macchiato=2, hot_chocolate=4
- RUN prints the café display AFTER EACH TURN (quantum).
- RUN steps must satisfy 1 ≤ steps ≤ (#queues).
- Disallowed for the core queue: collections.deque, queue.Queue, third-party DS.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


# Required menu items; you may add more keys for your own tests/experiments.
REQUIRED_MENU: Dict[str, int] = {
    "americano": 2,
    "latte": 3,
    "cappuccino": 3,
    "mocha": 4,
    "tea": 1,
    "macchiato": 2,
    "hot_chocolate": 4,
}


@dataclass
class Task:
    task_id: str
    remaining: int


class QueueRR:
    """
    Implement a FIFO queue from scratch (no deque/Queue for the core).
    A circular buffer or two-stack queue are fine choices.
    """

    def __init__(self, queue_id: str, capacity: int) -> None:
        # TODO: initialize your internal storage, size/capacity tracking, etc.
        if capacity < 0:
            raise ValueError("Capacity must be non-negative")
        self.queue_id = queue_id
        self.capacity = capacity
        self._storage: List[Optional[Task]] = [None] * capacity
        self._head: int = 0
        self._tail: int = 0
        self._size: int = 0

    def is_full(self) -> bool:
        """Return True if full; False if not full."""
        return self._size == self.capacity

    def is_empty(self) -> bool:
        """Return True if empty; False if not empty."""
        return self._size == 0

    def enqueue(self, task: Task) -> bool:
        """Return True on success; False if full (no mutation if full)."""
        if self.is_full():
            return False
        self._storage[self._tail] = task
        self._tail = (self._tail + 1) % self.capacity
        self._size += 1
        return True

    def dequeue(self) -> Optional[Task]:
        """Remove and return the front task; return None if empty."""
        if self.is_empty():
            return None
        task = self._storage[self._head]
        self._head = (self._head + 1) % self.capacity
        self._size -= 1
        return task

    def __len__(self) -> int:  # pragma: no cover - trivial when implemented
        return self._size

    def __iter__(self):
        for i in range(self._size):
            index = (self._head + i) % self.capacity
            yield self._storage[index]


class Scheduler:
    """
    Orchestrates multiple QueueRR instances in creation order.
    Maintains:
      - current time (minutes)
      - per-queue auto-incrementing counters for task ids
      - per-queue pending SKIP flags
      - RR pointer for the next queue to visit
    """

    def __init__(self) -> None:
        # TODO: initialize time, queues (ordered), id_counters, skip flags, rr index.
        self._time: int = 0
        self._queues: Dict[str, QueueRR] = {}
        self._queue_order: List[str] = []
        self._task_counters: Dict[str, int] = {}
        self._skip_flags: Dict[str, bool] = {}
        self._next_queue_index: int = 0

    # ----- Menu / state helpers -----

    def menu(self) -> Dict[str, int]:
        """
        Return the current menu mapping. Start with REQUIRED_MENU exactly.
        You may return a copy to avoid external mutation.
        """
        return REQUIRED_MENU.copy()

    def next_queue(self) -> Optional[str]:
        """
        Return the queue_id that will be visited next (or None if no queues).
        """
        if not self._queue_order:
            return None
        return self._queue_order[self._next_queue_index]

    # ----- Commands -----

    def create_queue(self, queue_id: str, capacity: int) -> List[str]:
        """
        Log: time=<t> event=create queue=<queue_id>
        Creation order defines RR order.
        """
        if queue_id not in self._queues:
            new_queue = QueueRR(queue_id, capacity)
            self._queues[queue_id] = new_queue
            self._queue_order.append(queue_id)
            self._task_counters[queue_id] = 1
            self._skip_flags[queue_id] = False

        log_message = f"time={self._time} event=create queue={queue_id}"
        return [log_message]

    def enqueue(self, queue_id: str, item_name: str) -> List[str]:
        """
        Behavior:
          - If item_name not in menu: print "Sorry, we don't serve that."
            and log reject with reason=unknown_item.
          - Else construct next task id as <queue_id>-NNN and try to enqueue:
              - On success: log enqueue with remaining=<burst>.
              - On full: print "Sorry, we're at capacity."
                and log reject with reason=full.
        """
        if item_name not in self.menu():
            print("Sorry, we don't serve that.")
            return [f"time={self._time} event=reject queue={queue_id} reason=unknown_item"]

        target_queue = self._queues.get(queue_id)
        # don't use truthiness on QueueRR (it defines __len__); check for None
        if target_queue is None:
            return [f"time={self._time} event=error reason=unknown_queue"]
        
        task_num = self._task_counters[queue_id]
        task_id = f"{queue_id}-{task_num:03d}"

        if target_queue.is_full():
            print("Sorry, we're at capacity.")
            log_message = f"time={self._time} event=reject queue={queue_id} task={task_id} reason=full"
            return [log_message]

        burst_time = self.menu()[item_name]
        new_task = Task(task_id=task_id, remaining=burst_time)
        target_queue.enqueue(new_task)
        self._task_counters[queue_id] += 1
        log_message = f"time={self._time} event=enqueue queue={queue_id} task={task_id} remaining={burst_time}"
        return [log_message]

    def mark_skip(self, queue_id: str) -> List[str]:
        """
        Mark the queue to be skipped on its next visit (does not advance time).
        Log: time=<t> event=skip queue=<queue_id>
        """
        if queue_id in self._queues:
            self._skip_flags[queue_id] = True
            return [f"time={self._time} event=skip queue={queue_id}"]
        return [f"time={self._time} event=error reason=unknown_queue"]

    def run(self, quantum: int, steps: Optional[int]) -> List[str]:
        """
        Execute up to 'steps' turns (each turn visits one queue) if provided,
        otherwise run until all queues are empty and no pending skips.

        Validate steps: 1 ≤ steps ≤ (#queues); otherwise:
          Log: time=<t> event=error reason=invalid_steps
          and do not perform any turns.

        Each visited queue should produce:
          - a run log:   time=<t> event=run queue=<qid>
          - zero-time transitions for empty/skip visits (no time advance)
          - if work occurs: time increases by min(remaining, quantum)
            and follow with work/finish logs as appropriate.
        """
        num_queues = len(self._queue_order)
        if num_queues == 0:
            return []

        if steps is not None and not (1 <= steps <= num_queues):
            return [f"time={self._time} event=error reason=invalid_steps"]

        logs = []
        turns_to_run = steps if steps is not None else float('inf')
        turns_done = 0

        # Loop for a specific number of steps or until the simulation should stop
        run_condition = True
        while run_condition:
            q_id = self.next_queue()
            if not q_id: break

            queue = self._queues[q_id]
            logs.append(f"time={self._time} event=run queue={q_id}")

            if self._skip_flags.get(q_id):
                self._skip_flags[q_id] = False
            elif not queue.is_empty():
                task = queue.dequeue()
                if task:
                    work_time = min(task.remaining, quantum)
                    self._time += work_time
                    task.remaining -= work_time

                    if task.remaining > 0:
                        queue.enqueue(task)
                        logs.append(f"time={self._time} event=work queue={q_id} task={task.task_id} remaining={task.remaining}")
                    else:
                        logs.append(f"time={self._time} event=finish queue={q_id} task={task.task_id}")

            self._next_queue_index = (self._next_queue_index + 1) % num_queues
            
            # Append display snapshot after each turn so the CLI can print it.
            # This ensures the display is produced after every RUN turn as required.
            disp = self.display()
            if disp:
                logs.extend(disp)
            turns_done += 1

            if steps is not None:
                if turns_done >= turns_to_run:
                    run_condition = False
            else:
                # If running until completion, check if all queues are empty and no skips are pending
                all_empty = all(q.is_empty() for q in self._queues.values())
                no_skips = not any(self._skip_flags.values())
                if all_empty and no_skips:
                    run_condition = False
        return logs


    # ----- Display -----

    def display(self) -> List[str]:
        """
        Return a compact snapshot with the exact lines/format:

          display time=<t> next=<qid_or_none>
          display menu=[name:minutes,...sorted by name...]
          display <qid> [n/cap][ skip] -> [task:rem,task:rem,...]
          ...

        NOTE: The CLI prints this after EACH RUN TURN only.
        """
        lines = []
        next_q = self.next_queue() or "none"
        lines.append(f"display time={self._time} next={next_q}")

        menu_items = sorted(self.menu().items())
        menu_str = ",".join([f"{k}:{v}" for k, v in menu_items])
        lines.append(f"display menu=[{menu_str}]")

        for q_id in self._queue_order:
            queue = self._queues[q_id]
            cap = queue.capacity
            size = len(queue)
            skip_str = " [ skip]" if self._skip_flags.get(q_id) else ""
            tasks_list = []
            for task in queue:
                if task:
                    tasks_list.append(f"{task.task_id}:{task.remaining}")
            tasks_str = ",".join(tasks_list)
            lines.append(f"display {q_id} [{size}/{cap}]{skip_str} -> [{tasks_str}]")

        return lines