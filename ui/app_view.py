"""
Solo Leveling UI — ui/app_view.py
Flet 0.24.0 compatible view:
profiles, HUD, standard quests, timed focus quest, and dungeon.

The focus timer uses page.run_task() and asyncio.sleep().
"""

import asyncio
import math
import os
import sys

import flet as ft

# Make the project root importable when running gui_main.py directly.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


from core.models import Player, Quest, QuestStatus
from services.dungeon_service import generate_dungeon_run
from services.storage_service import StorageService

TICK_COUNT = 60
RING_DIAMETER = 140
STACK_SIZE = 200
CENTER_OFFSET = STACK_SIZE / 2
DOT_SIZE = 8

COLOR_ACTIVE = "#00e5ff"
COLOR_INACTIVE = "#12324a"
COLOR_ACCENT = "#a855f7"
GLASS_BG = "#0a0f1e"

FLOOR_CAP = 20
XP_PER_FLOOR = 25


def _snack(page: ft.Page, message: str, ok: bool = True) -> None:
    """Show a short status message."""
    snack = ft.SnackBar(
        content=ft.Text(
            message,
            color="#0a0f1e" if ok else "#ffffff",
            weight=ft.FontWeight.BOLD,
        ),
        bgcolor=COLOR_ACTIVE if ok else COLOR_ACCENT,
        duration=3000,
    )
    page.open(snack)


def validate_minutes(value: str | None) -> float | None:
    """Return positive finite minutes, or None for invalid input."""
    try:
        minutes = float(value or "")
    except (TypeError, ValueError):
        return None

    if not math.isfinite(minutes) or minutes <= 0:
        return None

    return minutes


def validate_nonnegative_int(value: str | None) -> int | None:
    """Return a non-negative integer, or None for invalid input."""
    try:
        number = float(value or "")
    except (TypeError, ValueError):
        return None

    if not math.isfinite(number) or not number.is_integer() or number < 0:
        return None

    return int(number)


def validate_positive_int(value: str | None) -> int | None:
    """Return a positive integer, or None for invalid input."""
    number = validate_nonnegative_int(value)
    if number is None or number == 0:
        return None
    return number


class SoloLevelingView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.player: Player | None = None
        self.current_profile_name: str | None = None

        self.timer_running = False
        self.timer_task_started = False
        self.timer_total = 0.0
        self.timer_remaining = 0.0
        self.timer_quest_title = ""

        self._build_ui()

    def _build_ui(self) -> None:
        self.page.bgcolor = GLASS_BG
        self.page.title = "Solo Leveling — Hunter System"
        self.page.padding = 20

        # Profile controls
        self.profile_dropdown = ft.Dropdown(
            label="Select Hunter Profile",
            width=280,
            options=[],
            on_change=self._on_profile_selected,
        )
        self.new_profile_field = ft.TextField(
            label="New Hunter Name",
            width=180,
            hint_text="e.g. Sung Jin-Woo",
        )
        self.create_profile_btn = ft.ElevatedButton(
            "＋ Create Profile",
            on_click=self._on_create_profile,
        )

        # Player HUD
        self.name_text = ft.Text(
            "—",
            size=26,
            weight=ft.FontWeight.BOLD,
            color=COLOR_ACTIVE,
        )
        self.rank_text = ft.Text(
            "Rank: —",
            color=COLOR_ACCENT,
            weight=ft.FontWeight.BOLD,
        )
        self.level_text = ft.Text("Level: —", color="#ffffff")
        self.exp_text = ft.Text("EXP: —", color="#9fb8c8")
        self.progress_bar = ft.ProgressBar(
            value=0,
            width=320,
            color=COLOR_ACTIVE,
            bgcolor="#12324a",
        )

        # Standard quests
        self.quest_title_field = ft.TextField(
            label="Quest Title",
            width=280,
        )
        self.quest_exp_field = ft.TextField(
            label="EXP Reward",
            width=120,
            hint_text="e.g. 50",
        )
        self.add_quest_btn = ft.ElevatedButton(
            "Add Quest",
            on_click=self._on_add_quest,
        )
        self.quests_list = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

        # Timed focus quest
        self.timer_minutes_field = ft.TextField(
            label="Minutes",
            width=100,
            hint_text="25",
            value="25",
        )
        self.timer_title_field = ft.TextField(
            label="Focus Quest Title",
            width=170,
            hint_text="Deep Work",
        )
        self.timer_start_btn = ft.ElevatedButton(
            "▶ Start Focus",
            on_click=self._on_start_timer,
        )
        self.timer_abort_btn = ft.ElevatedButton(
            "■ Abort",
            on_click=self._on_abort_timer,
            disabled=True,
        )
        self.countdown_text = ft.Text(
            "00:00",
            size=30,
            weight=ft.FontWeight.BOLD,
            color=COLOR_ACTIVE,
        )
        self.timer_status_text = ft.Text(
            "Ready",
            color="#9fb8c8",
            size=12,
        )
        self.ring = self._build_segmented_ring()

        # Dungeon
        self.dungeon_log = ft.Text(
            "",
            color="#9fb8c8",
            size=12,
            selectable=True,
            expand=True,
        )
        self.dungeon_floors_field = ft.TextField(
            label="Floors",
            width=80,
            value="5",
        )
        self.dungeon_btn = ft.ElevatedButton(
            "⚔ Enter Dungeon",
            on_click=self._on_enter_dungeon,
        )

        # Page layout
        self.page.add(
            ft.Column(
                [
                    ft.Row(
                        [
                            self.profile_dropdown,
                            self.new_profile_field,
                            self.create_profile_btn,
                        ],
                        wrap=True,
                        spacing=8,
                    ),
                    ft.Divider(color="#12324a"),
                    ft.Container(
                        ft.Column(
                            [
                                self.name_text,
                                self.rank_text,
                                self.level_text,
                                self.exp_text,
                                self.progress_bar,
                            ]
                        ),
                        padding=16,
                        border_radius=16,
                        bgcolor=ft.colors.with_opacity(0.08, "#ffffff"),
                        border=ft.border.all(1, "#1e3a5f"),
                    ),
                    ft.Divider(color="#12324a"),
                    ft.Text(
                        "STANDARD QUESTS",
                        color=COLOR_ACCENT,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        [
                            self.quest_title_field,
                            self.quest_exp_field,
                            self.add_quest_btn,
                        ],
                        wrap=True,
                        spacing=8,
                    ),
                    self.quests_list,
                    ft.Divider(color="#12324a"),
                    ft.Text(
                        "TIMED FOCUS QUEST",
                        color=COLOR_ACCENT,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        [self.timer_minutes_field, self.timer_title_field],
                        wrap=True,
                        spacing=8,
                    ),
                    ft.Row(
                        [
                            self.timer_start_btn,
                            self.timer_abort_btn,
                            self.timer_status_text,
                        ],
                        spacing=8,
                    ),
                    ft.Container(
                        self.ring,
                        alignment=ft.alignment.center,
                        padding=10,
                    ),
                    ft.Divider(color="#12324a"),
                    ft.Text(
                        "DUNGEON",
                        color=COLOR_ACCENT,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        [self.dungeon_floors_field, self.dungeon_btn],
                        spacing=8,
                    ),
                    ft.Container(
                        self.dungeon_log,
                        padding=10,
                        height=140,
                        border_radius=12,
                        bgcolor=ft.colors.with_opacity(0.06, "#ffffff"),
                        border=ft.border.all(1, "#1e3a5f"),
                    ),
                ],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        )

        self._refresh_profiles()

    # ------------------------------------------------------------------
    # Segmented timer ring
    # ------------------------------------------------------------------
    def _build_segmented_ring(self) -> ft.Stack:
        self.dots: list[ft.Container] = []
        radius = RING_DIAMETER / 2
        controls = []

        for index in range(TICK_COUNT):
            angle = 2 * math.pi * index / TICK_COUNT - math.pi / 2
            center_x = CENTER_OFFSET + radius * math.cos(angle)
            center_y = CENTER_OFFSET + radius * math.sin(angle)

            dot = ft.Container(
                width=DOT_SIZE,
                height=DOT_SIZE,
                border_radius=DOT_SIZE / 2,
                bgcolor=COLOR_INACTIVE,
                left=center_x - DOT_SIZE / 2,
                top=center_y - DOT_SIZE / 2,
            )
            self.dots.append(dot)
            controls.append(dot)

        controls.append(
            ft.Container(
                ft.Column(
                    [self.countdown_text, self.timer_status_text],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                width=STACK_SIZE,
                height=STACK_SIZE,
                alignment=ft.alignment.center,
            )
        )

        return ft.Stack(
            controls,
            width=STACK_SIZE,
            height=STACK_SIZE,
        )

    def _update_ring(self, fraction_active: float) -> None:
        fraction_active = max(0.0, min(1.0, fraction_active))
        active_count = round(fraction_active * TICK_COUNT)

        for index, dot in enumerate(self.dots):
            dot.bgcolor = COLOR_ACTIVE if index < active_count else COLOR_INACTIVE

    @staticmethod
    def _format_mmss(seconds: float) -> str:
        remaining = max(0, int(round(seconds)))
        return f"{remaining // 60:02d}:{remaining % 60:02d}"

    # ------------------------------------------------------------------
    # Profiles
    # ------------------------------------------------------------------
    def _refresh_profiles(self) -> None:
        names = StorageService.list_profiles()
        self.profile_dropdown.options = [ft.dropdown.Option(name) for name in names]
        self.page.update()

    def _on_create_profile(self, e) -> None:
        name = (self.new_profile_field.value or "").strip()
        if not name:
            _snack(self.page, "Hunter name cannot be empty.", ok=False)
            return

        if name in StorageService.list_profiles():
            _snack(self.page, "Profile already exists.", ok=False)
            return

        player = Player(name=name)
        StorageService.save_profile(player)

        self.new_profile_field.value = ""
        self._refresh_profiles()
        self.profile_dropdown.value = name
        self._load_player(name)
        _snack(self.page, f"Hunter '{name}' awakened!")

    def _on_profile_selected(self, e) -> None:
        name = self.profile_dropdown.value
        if name:
            self._load_player(name)

    def _load_player(self, name: str) -> None:
        self.current_profile_name = name
        self.player = StorageService.load_profile(name)

        if self.player is None:
            _snack(self.page, f"Profile '{name}' not found.", ok=False)
            return

        self._refresh_hud()
        self._refresh_quests()

    def _refresh_hud(self) -> None:
        if not self.player:
            return

        self.name_text.value = self.player.name
        self.rank_text.value = f"Rank: {self.player.rank}"
        self.level_text.value = f"Level: {self.player.level}"
        self.exp_text.value = (
            f"EXP: {self.player.exp} / {self.player.exp_to_next_level}"
        )

        exp_target = self.player.exp_to_next_level
        self.progress_bar.value = self.player.exp / exp_target if exp_target else 0
        self.page.update()

    # ------------------------------------------------------------------
    # Standard quests
    # ------------------------------------------------------------------
    def _refresh_quests(self) -> None:
        if not self.player:
            return

        rows = []
        for quest in self.player.quests:
            completed = quest.status == QuestStatus.COMPLETED

            row_controls = [
                ft.Text(
                    ("✔ " if completed else "• ") + quest.title,
                    color="#4ade80" if completed else "#ffffff",
                    expand=True,
                ),
                ft.Text(
                    f"+{quest.exp_reward} XP",
                    color=COLOR_ACTIVE,
                    size=12,
                ),
            ]

            if not completed:
                row_controls.append(
                    ft.ElevatedButton(
                        "Complete",
                        on_click=lambda e, q=quest: self._complete_quest(q),
                    )
                )

            rows.append(ft.Row(row_controls, spacing=8))

        self.quests_list.controls = rows or [ft.Text("No quests yet.", color="#64748b")]
        self.page.update()

    def _on_add_quest(self, e) -> None:
        if not self.player:
            _snack(self.page, "Select a hunter profile first.", ok=False)
            return

        title = (self.quest_title_field.value or "").strip()
        exp = validate_nonnegative_int(self.quest_exp_field.value or "0")

        if not title:
            _snack(self.page, "Quest title cannot be empty.", ok=False)
            return

        if exp is None:
            _snack(self.page, "EXP must be a non-negative integer.", ok=False)
            return

        quest = Quest(title=title, exp_reward=exp)
        self.player.quests.append(quest)
        StorageService.save_profile(self.player)

        self.quest_title_field.value = ""
        self.quest_exp_field.value = ""
        self._refresh_hud()
        self._refresh_quests()
        _snack(self.page, f"Quest '{title}' registered!")

    def _complete_quest(self, quest: Quest) -> None:
        if not self.player:
            _snack(self.page, "Select a hunter profile first.", ok=False)
            return

        if quest.status == QuestStatus.COMPLETED:
            return

        quest.status = QuestStatus.COMPLETED
        self.player.add_exp(quest.exp_reward)
        StorageService.save_profile(self.player)

        self._refresh_hud()
        self._refresh_quests()
        _snack(
            self.page,
            f"Quest completed! +{quest.exp_reward} XP earned.",
        )

    # ------------------------------------------------------------------
    # Timed focus quest
    # ------------------------------------------------------------------
    def _on_start_timer(self, e) -> None:
        if self.timer_running:
            _snack(self.page, "Focus timer already running.", ok=False)
            return

        if not self.player:
            _snack(self.page, "Select a hunter profile first.", ok=False)
            return

        minutes = validate_minutes(self.timer_minutes_field.value)
        title = (self.timer_title_field.value or "").strip() or "Focus Quest"

        if minutes is None:
            _snack(
                self.page,
                "Minutes must be a positive finite number.",
                ok=False,
            )
            return

        self.timer_total = minutes * 60.0
        self.timer_remaining = self.timer_total
        self.timer_quest_title = title
        self.timer_running = True
        self.timer_task_started = False

        self.timer_start_btn.disabled = True
        self.timer_abort_btn.disabled = False
        self.timer_status_text.value = "Focusing…"
        self.countdown_text.color = COLOR_ACTIVE
        self.countdown_text.value = self._format_mmss(self.timer_remaining)
        self._update_ring(1.0)
        self.page.update()

        self.page.run_task(self._timer_loop_async)

    async def _timer_loop_async(self) -> None:
        if self.timer_task_started:
            return

        self.timer_task_started = True
        try:
            while self.timer_running and self.timer_remaining > 0:
                await asyncio.sleep(1)

                if not self.timer_running:
                    break

                self.timer_remaining = max(0.0, self.timer_remaining - 1)
                fraction = (
                    self.timer_remaining / self.timer_total if self.timer_total else 0
                )
                self._update_ring(fraction)
                self.countdown_text.value = self._format_mmss(self.timer_remaining)
                self.page.update()

            if self.timer_running and self.timer_remaining <= 0:
                self._complete_focus_quest()
        finally:
            self.timer_task_started = False

    def _on_abort_timer(self, e) -> None:
        if not self.timer_running:
            return

        self.timer_running = False
        self._reset_timer_ui("Aborted")
        _snack(self.page, "Focus session aborted.", ok=False)

    def _complete_focus_quest(self) -> None:
        self.timer_running = False

        if not self.player:
            self._reset_timer_ui("Done")
            return

        minutes = max(1, int(self.timer_total // 60))
        reward = minutes * 10
        quest = Quest(
            title=f"[Focus] {self.timer_quest_title} ({minutes} min)",
            exp_reward=reward,
            status=QuestStatus.COMPLETED,
        )

        self.player.quests.append(quest)
        self.player.add_exp(reward)
        StorageService.save_profile(self.player)

        self._refresh_hud()
        self._refresh_quests()
        self._reset_timer_ui("Completed ✔")
        self.countdown_text.color = "#4ade80"
        self.page.update()
        _snack(self.page, f"Focus complete! +{reward} XP earned.")

    def _reset_timer_ui(self, status: str) -> None:
        self.timer_start_btn.disabled = False
        self.timer_abort_btn.disabled = True
        self.timer_status_text.value = status
        self.countdown_text.value = "00:00"
        self.countdown_text.color = COLOR_ACTIVE
        self._update_ring(0.0)
        self.page.update()

    # ------------------------------------------------------------------
    # Dungeon
    # ------------------------------------------------------------------
    def _on_enter_dungeon(self, e) -> None:
        if not self.player:
            _snack(self.page, "Select a hunter profile first.", ok=False)
            return

        floors = validate_positive_int(self.dungeon_floors_field.value)
        if floors is None:
            _snack(self.page, "Floors must be a positive integer.", ok=False)
            return

        floors = min(floors, FLOOR_CAP)
        lines = []
        total_exp = 0

        for room in generate_dungeon_run(floors):
            floor_no = int(room["floor"])
            reward = XP_PER_FLOOR
            total_exp += reward
            lines.append(
                f"✔ Floor {floor_no}: {room['info']} | "
                f"{room['difficulty']} | +{reward} XP"
            )

        lines.append(f"— Run complete: {len(lines)} floors, +{total_exp} XP total —")
        self.dungeon_log.value = "\n".join(lines)

        self.player.add_exp(total_exp)
        StorageService.save_profile(self.player)
        self._refresh_hud()
        self.page.update()

        _snack(
            self.page,
            f"Dungeon cleared! +{total_exp} XP " f"(+{XP_PER_FLOOR}/floor).",
        )


def main(page: ft.Page) -> None:
    page.theme_mode = ft.ThemeMode.DARK
    SoloLevelingView(page)


if __name__ == "__main__":
    ft.app(target=main)
