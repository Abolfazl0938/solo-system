
```markdown
# ⚡ SoloSystem

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-pytest%20100%25%20passed-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Architecture](https://img.shields.io/badge/design-Clean%20Architecture-orange.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, terminal-based CLI system inspired by the world of **Solo Leveling**. Built completely from scratch in Python to master core-to-advanced software engineering concepts: clean OOP architecture, custom decorators, lazy generators, atomic state transactions with automatic rollback mechanisms, non-blocking asynchronous concurrency, persistent file storage, and automated testing with `pytest`.

---

## 📖 About

In the *Solo Leveling* universe, awakened hunters receive daily quests, progress through experience points, scan mysterious dimensional gates, and conquer perilous dungeon floors.

**SoloSystem** brings these mechanics to life directly in your terminal. Every game mechanism serves as an applied demonstration of an advanced Python concept:
- **Hunter Profile & Inventory:** Built using Python Dunder protocols (`__len__`, `__getitem__`, `__iter__`, `__contains__`).
- **Dungeon Progression:** Uses lazy generators (`yield`) to stream floor data dynamically without heavy memory consumption.
- **Quest & Dungeon Transactions:** Safeguarded by custom context managers ensuring atomic rollback to prior snapshots if errors occur.
- **Dimensional Gate Scanning:** Non-blocking multi-gate reconnaissance powered by Python's `asyncio.gather`.
- **Data Persistence:** Automated load/save mechanism using `pathlib.Path` and structured JSON serialization.

---

## ✨ Features

- **Dynamic Hunter Profile:** Real-time level calculation, EXP bar updates, automatic rank adjustments (from E-Rank up to S-Rank), and active quest counters.
- **Daily Quests System:** Register, complete, and track quests with atomic transaction safety.
- **Lazy Dungeon Generator:** Procedural, memory-efficient floor clearance with real-time execution timing decorators.
- **Concurrent Gate Radar:** Parallel gate scanning leveraging AsyncIO workers to minimize I/O wait times.
- **Auto-Persistence:** Preserves your hunter profile, stats, and completed quests between CLI restarts.
- **Automated Pytest Suite:** Complete automated test suite covering models, context managers, async routines, generators, and storage.

---

## 🛠️ Technologies & Tools

- **Core:** Python 3.10+
- **CLI Interface:** `rich` (formatted panels, status bars, and tables)
- **Concurrency:** `asyncio`
- **Testing:** `pytest`
- **File Management:** `pathlib`, `json`
- **Metaprogramming:** `functools.wraps`

---

## ⚙️ Installation (Step-by-Step)

Follow these steps to set up and run the project locally on your machine:

### 1. Clone the Repository
Open your terminal and clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/solo-system.git
cd solo-system
```

### 2. Create and Activate a Virtual Environment
Isolating dependencies ensures a clean working environment:

- **On Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
Install all required libraries using pip:
```bash
pip install -r requirements.txt
```

---

## 🎮 How to Use (Step-by-Step Guide)

Run the application with:
```bash
python main.py
```

### Main Menu Navigation
Once the application launches, the **Hunter System CLI** dashboard displays with an interactive numeric menu:

```text
========================================
           SOLO SYSTEM TERMINAL         
========================================
[1] View Hunter Status
[2] Add Daily Quest
[3] Complete a Quest
[4] Enter Dungeon (Lazy Generator)
[5] Scan Dimensional Gates (AsyncIO)
[6] Save & Exit
```

### Step-by-Step Walkthrough:

1. **Check Hunter Status (`Option 1`):**
   - Displays your hunter's Name, Level, Rank, EXP bar, and current active/completed quests.
2. **Add a Daily Quest (`Option 2`):**
   - Enter a quest title (e.g., `100 Push-ups`) and EXP reward (e.g., `50`).
   - The system validates and commits the quest safely via an atomic transaction.
3. **Complete a Quest (`Option 3`):**
   - Lists pending quests by index. Enter the corresponding index to claim EXP and trigger level calculation.
4. **Enter Dungeon (`Option 4`):**
   - Enter the target floor count. Floors are generated on-the-fly via a lazy generator, simulating battle encounters and granting clear rewards.
5. **Scan Dimensional Gates (`Option 5`):**
   - Launches an asynchronous multi-scanner. Multiple gates are surveyed simultaneously, logging ranks and completion states in parallel.
6. **Save & Exit (`Option 6`):**
   - Serializes the current hunter state and quest history into `data/player_save.json` and cleanly exits the program.

---

## 🧪 Running Automated Tests

SoloSystem includes a comprehensive `pytest` test suite verifying all modules:

```bash
pytest -v
```

Expected Output:
```text
tests/test_context_managers.py::test_quest_transaction_success PASSED
tests/test_context_managers.py::test_quest_transaction_rollback_on_failure PASSED
tests/test_context_managers.py::test_dungeon_raid_session_success PASSED
tests/test_dungeon_service.py::test_generate_dungeon_run_is_generator PASSED
tests/test_dungeon_service.py::test_generate_dungeon_run_output PASSED
tests/test_models.py::test_quest_initialization_and_serialization PASSED
tests/test_models.py::test_player_exp_and_level_up PASSED
tests/test_models.py::test_player_container_dunder_methods PASSED
tests/test_network_service.py::test_network_scan_all_gates PASSED
tests/test_storage_service.py::test_storage_save_and_load PASSED

============================== 10 passed in 0.42s ==============================
```

---

## 📂 Project Structure

```text
solo-system/
│
├── core/
│   ├── __init__.py
│   ├── models.py            # Hunter & Quest domain entities, Dunder container methods
│   ├── decorators.py        # Custom decorators for access control & execution benchmarking
│   └── context_managers.py  # Atomic quest transactions & raid sessions with rollback
│
├── services/
│   ├── __init__.py
│   ├── dungeon_service.py   # Generator-based lazy dungeon floor streamer
│   ├── network_service.py   # Concurrent AsyncIO gate reconnaissance service
│   └── storage_service.py   # Safe JSON & Pathlib persistence engine
│
├── tests/
│   ├── test_models.py
│   ├── test_context_managers.py
│   ├── test_dungeon_service.py
│   ├── test_network_service.py
│   └── test_storage_service.py
│
├── data/                    # JSON save files directory
├── main.py                  # Rich-powered interactive CLI entry point
├── requirements.txt         # Project dependencies
├── .gitignore               # Ignored cache and virtual environment files
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

## 🎯 Learning Goals & Python Mastery

Through building **SoloSystem**, the following computer science and Python concepts were implemented and verified:

- **Object-Oriented Programming (OOP):** Encapsulation, abstraction, and custom Dunder protocols (`__len__`, `__getitem__`, `__iter__`, `__contains__`).
- **Metaprogramming & Decorators:** Function wrappers, preserving function metadata via `functools.wraps`, and benchmarking execution times.
- **Lazy Evaluation & Generators:** Efficient memory allocation using `yield` for unbounded or large-scale data iteration.
- **Atomic State Transactions:** Managing setup, safe execution, and error rollback using custom Python Context Managers (`__enter__` / `__exit__`).
- **Asynchronous Concurrency:** Managing non-blocking I/O routines using Python's `asyncio` and `asyncio.gather`.
- **Clean Architecture & File I/O:** Decoupling storage logic with `pathlib.Path` and handling JSON serialization/deserialization.
- **Test-Driven Reliability:** Writing automated unit tests using `pytest` to guarantee system stability and prevent regression bugs.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
```
