
# ⚔️ Solo Leveling — Hunter System

A gamified desktop productivity application built with **Python** and **Flet**, inspired by the *Solo Leveling* universe. Turn your real-life tasks into active quests, conquer dungeons, earn EXP, level up, and use the built-in focus timer to stay disciplined.

---

## 🎯 Project Goals

- **Gamification of Daily Tasks:** Convert tasks and habits into manageable quests with custom EXP rewards.
- **Visual Progression:** Track your personal growth with real-time level progression, rank evaluation, and dynamic EXP progress bars.
- **Deep Focus:** Dedicated focus quest mode with a visual countdown timer to eliminate distractions.
- **Dungeon Challenges:** Custom floor-based dungeon challenges for intense multi-step goals.

---

## ✨ Features

- 👤 **Hunter Management:** Create multiple hunter profiles and switch between them seamlessly.
- 📊 **Dynamic Status Bar:** Real-time visual progress bar tracking current EXP and required EXP to level up.
- 📜 **Active Quests:** Add custom quests with specific EXP rewards and mark them completed.
- ⏱️ **Focus Quest & Timer:** Set a focus duration (e.g., 25 minutes) with visual countdown, Start, and Abort controls.
- 🚪 **Dungeon Gate:** Configure dungeon floor count and enter focused challenge sessions.
- 🎨 **Modern Dark UI:** Responsive and sleek neon/dark theme inspired by RPG interfaces.

---

## 🚀 Installation & Setup

Follow these steps to run the application locally on Windows:

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/solo-system.git
cd solo-system
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python gui_main.py
```

---

## 📖 Step-by-Step User Guide

1. **Select or Create a Hunter:**
   - Type your name in `New Hunter Name` and click **+ Create**.
   - Use the dropdown `Select Hunter` to switch between saved profiles.
2. **Add & Complete Active Quests:**
   - Enter a task name in `Quest Title` and assign its EXP in the `EXP` field.
   - Click **Add**. Completed quests reward EXP and advance your Hunter Level/Rank.
3. **Run a Focus Session:**
   - Enter your task in `Focus Quest Title`.
   - Set the duration in `Min` (default is 25).
   - Click **▶ Start** to begin the timer. Click **⏹ Abort** if you need to cancel.
4. **Enter Dungeons:**
   - Set your desired floor count in `Floors` and click **⚔️ Enter Dungeon** to start your challenge.

---

## 📦 Building Standalone Executable (.exe)

To build a standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name "SoloSystem" gui_main.py
```

The output file will be generated in `dist/SoloSystem.exe`.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **GUI Framework:** [Flet](https://flet.dev/) (Flutter for Python)
- **Data Persistence:** Local JSON Storage
