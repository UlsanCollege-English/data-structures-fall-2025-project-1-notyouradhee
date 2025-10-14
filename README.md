
# Multi-Queue Round-Robin Café (Interactive CLI)

This project simulates a busy campus café that serves multiple customer lines (e.g., Mobile, Walk-Ins, Faculty) using a fair round-robin scheduling algorithm. Instead of serving one line completely, the barista processes one order from each line for a fixed time slice, called a quantum, before cycling to the next.

This command-line application is built from scratch in Python and demonstrates core data structure and algorithm concepts.

Key Features:

Fair Round-Robin Scheduling: Processes tasks from multiple queues in a fixed, cyclical order.

From-Scratch Queue: Implements a high-performance circular buffer for all queue operations, without using built-in libraries like collections.deque.

Preemptive Simulation: Tasks that are not completed within a quantum are correctly placed at the end of their line to resume later.

Interactive CLI: A simple, command-driven interface to manage the café simulation.

Deterministic Logging & Display: Provides precise, turn-by-turn updates on the café's status for easy debugging and verification


## 🧠 Example Use Case

CREATE Mobile 3

CREATE WalkIns 2

ENQ Mobile latte

ENQ WalkIns americano

SKIP WalkIns

RUN 2


Displays after each turn:

display time=3 next=WalkIns

display menu=[americano:2,cappuccino:3,hot_chocolate:4,latte:3,macchiato:2,mocha:4,tea:1]

display Mobile [0/3] -> []

display WalkIns [1/2][ skip] -> [WalkIns-001:2]

## How to run

From the **root project folder**, run:

### Windows 

python .\src\cli.py

### macOS / Linux (Bash)

python3 src/cli.py

Type your commands. End the session with a blank line.

## ⚙️ Commands
The café simulation is controlled by four simple commands.

Command	Description

CREATE <queue_id> <capacity>  - Creates a new order line with a given name and maximum capacity. The order of creation determines the  round-robin sequence.

ENQ <queue_id> <item_name> - Adds a new drink order to the back of a specified queue. The system automatically assigns a task ID in the format <queue_id>-NNN (e.g., Mobile-001).

SKIP <queue_id>	 - Marks a queue to be skipped one time on its next turn. This action is instant and does not advance the simulation clock.

RUN <quantum> [steps] -	Starts the round-robin scheduler. <quantum> is the time (in minutes) spent on each task per turn. The optional [steps] argument runs the simulation for a specific number of turns; if omitted, it runs until all queues are empty.


## How to run tests locally

We use pytest for automated testing.

1. Install pytest if needed:
pip install pytest

2. Run the tests:

Make sure your PYTHONPATH includes the src/ folder.

Windows

pytest -q

or,

python -m pytest -q 

macOS / Linux

export PYTHONPATH=src
pytest -q


✅ You should see all tests as PASSED.




## Complexity Notes
Queue Implementation
The core queue data structure is a circular buffer implemented from scratch using a pre-allocated Python list and integer pointers for the head and tail. This design was chosen to meet the project requirement of not using standard library queues (deque, queue.Queue) while achieving high performance for FIFO operations.

Time Complexity
enqueue: Amortized O(1). Adding an item involves updating an array element at the tail index and incrementing the pointer, which is a constant-time operation.

dequeue: Amortized O(1). Removing an item only requires retrieving an element at the head index and incrementing the pointer, also a constant-time operation.

run: O(#turns + total_minutes_worked). The scheduler's runtime is proportional to the number of turns it executes, plus the cumulative time spent processing all tasks, as each minute of work is simulated.

Space Complexity
O(N), where N is the total number of tasks that can be held across all queues at maximum capacity. The space is dominated by the storage required for the tasks and the metadata for each queue.

##🧾 Menu Items
Hardcoded Menu 
The menu is fixed as follows:

| Item          | Time (min) |
| ------------- | ---------- |
| americano     | 2          |
| latte         | 3          |
| cappuccino    | 3          |
| mocha         | 4          |
| tea           | 1          |
| macchiato     | 2          |
| hot_chocolate | 4          |

## System Policies
Rejection Messages: The system provides exact messages for specific failures:

Sorry, we don't serve that. (for unknown menu items)

Sorry, we're at capacity. (for full queues)

Display Updates: The café status board is printed only after each turn of a RUN command.

RUN Steps Validation: The steps argument for RUN, if provided, must satisfy 1 ≤ steps ≤ (# of queues).


## Project Structure 

src/
├── cli.py               # CLI interface (user input)
├── parser.py            # Command parser
├── scheduler.py         # Scheduler + queue logic
tests/
├── public               # Provided test cases
README.md                # This file

## 👨‍💻 Authors

Owner: notyouradhee

Assigned By: Prof. Benjamin William Slater

Course: Data Structures – Fall 2025

College: Ulsan College, South Korea




