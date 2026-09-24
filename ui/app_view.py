"""
Solo Leveling UI — ui/app_view.py
Flet 0.24.0 compact desktop layout:
Two-column HUD & Quest dashboard, centered circular focus timer,
dungeon log, and local JSON profile storage.
"""

import asyncio
import math
import os
import sys

import flet as ft

# Make the project root importable when running directly
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.models import Player, Quest, QuestStatus
from services.dungeon_service import generate_dungeon_run
from services.storage_service import StorageService

TICK_COUNT = 60
RING_DIAMETER = 130
STACK_SIZE = 160
CENTER_OFFSET = STACK_SIZE / 2
DOT_SIZE = 7

COLOR_ACTIVE = "#00e5ff"
COLOR_INACTIVE = "#12324a"
COLOR_ACCENT = "#a855f7"
COLOR_SUCCESS = "#4ade80"
GLASS_BG = "#0a0f1e"
CARD_BG = "#0f172a"
BORDER_COLOR = "#1e3a5f"

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
        self.page.padding = 14
        self.page.spacing = 10

        # Profile selection
        self.profile_dropdown = ft.Dropdown(
            label="Select Hunter",
            height=40,
            content_padding=8,
            text_size=13,
            options=[],
            on_change=self._on_profile_selected,
            expand=True,
        )
        self.new_profile_field = ft.TextField(
            label="New Hunter Name",
            height=40,
            content_padding=8,
            text_size=13,
            hint_text="e.g. Sung Jin-Woo",
            expand=True,
        )
        self.create_profile_btn = ft.ElevatedButton(
            "＋ Create",
            height=40,
            on_click=self._on_create_profile,
        )

        # Player HUD
        self.name_text = ft.Text(
            "—", size=22, weight=ft.FontWeight.BOLD, color=COLOR_ACTIVE
        )
        self.rank_text = ft.Text(
            "Rank: —", size=13, color=COLOR_ACCENT, weight=ft.FontWeight.BOLD
        )
        self.level_text = ft.Text(
            "Level: —", size=13, color="#ffffff", weight=ft.FontWeight.BOLD
        )
        self.exp_text = ft.Text("EXP: —", size=12, color="#9fb8c8")
        self.progress_bar = ft.ProgressBar(
            value=0, height=8, color=COLOR_ACTIVE, bgcolor="#12324a"
        )

        # Quests Controls
        self.quest_title_field = ft.TextField(
            label="Quest Title",
            height=38,
            content_padding=8,
            text_size=13,
            expand=True,
        )
        self.quest_exp_field = ft.TextField(
            label="EXP",
            width=70,
            height=38,
            content_padding=8,
            text_size=13,
            hint_text="50",
        )
        self.add_quest_btn = ft.ElevatedButton(
            "Add", height=38, on_click=self._on_add_quest
        )
        self.quests_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)

        # Timed Focus Controls
        self.timer_minutes_field = ft.TextField(
            label="Min",
            width=65,
            height=38,
            content_padding=8,
            text_size=13,
            value="25",
        )
        self.timer_title_field = ft.TextField(
            label="Focus Quest Title",
            height=38,
            content_padding=8,
            text_size=13,
            hint_text="Deep Work",
            expand=True,
        )
        self.timer_start_btn = ft.ElevatedButton(
            "▶ Start", height=34, on_click=self._on_start_timer
        )
        self.timer_abort_btn = ft.ElevatedButton(
            "■ Abort", height=34, on_click=self._on_abort_timer, disabled=True
        )
        self.timer_status_text = ft.Text("Ready", color="#9fb8c8", size=12)

        # Dedicated centered text inside ring
        self.countdown_text = ft.Text(
            "00:00",
            size=26,
            weight=ft.FontWeight.BOLD,
            color=COLOR_ACTIVE,
            text_align=ft.TextAlign.CENTER,
        )
        self.ring = self._build_segmented_ring()

        # Dungeon Controls
        self.dungeon_floors_field = ft.TextField(
            label="Floors",
            width=70,
            height=38,
            content_padding=8,
            text_size=13,
            value="5",
        )
        self.dungeon_btn = ft.ElevatedButton(
            "⚔ Enter Dungeon", height=38, on_click=self._on_enter_dungeon
        )
        self.dungeon_log = ft.Text("", color="#9fb8c8", size=11, selectable=True)

        # Assembly: Left Panel (Profile + HUD + Dungeon)
        left_panel = ft.Container(
            content=ft.Column(
                [
                    # Top profile selector row
                    ft.Row(
                        [
                            self.profile_dropdown,
                            self.new_profile_field,
                            self.create_profile_btn,
                        ],
                        spacing=6,
                    ),
                    # Hunter HUD Card
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        self.name_text,
                                        ft.Row(
                                            [self.rank_text, self.level_text],
                                            spacing=10,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                self.exp_text,
                                self.progress_bar,
                            ],
                            spacing=6,
                        ),
                        padding=12,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER_COLOR),
                    ),
                    # Dungeon Card
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "DUNGEON GATE",
                                    size=13,
                                    color=COLOR_ACCENT,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Row(
                                    [self.dungeon_floors_field, self.dungeon_btn],
                                    spacing=6,
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [self.dungeon_log], scroll=ft.ScrollMode.AUTO
                                    ),
                                    height=110,
                                    padding=8,
                                    border_radius=8,
                                    bgcolor=GLASS_BG,
                                    border=ft.border.all(1, "#12324a"),
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=12,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER_COLOR),
                        expand=True,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
            expand=1,
        )

        # Assembly: Right Panel (Quests + Centered Timer)
        right_panel = ft.Container(
            content=ft.Column(
                [
                    # Standard Quests Card
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "ACTIVE QUESTS",
                                    size=13,
                                    color=COLOR_ACCENT,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Row(
                                    [
                                        self.quest_title_field,
                                        self.quest_exp_field,
                                        self.add_quest_btn,
                                    ],
                                    spacing=6,
                                ),
                                ft.Container(
                                    content=self.quests_list,
                                    height=140,
                                    padding=6,
                                    border_radius=8,
                                    bgcolor=GLASS_BG,
                                    border=ft.border.all(1, "#12324a"),
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=12,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER_COLOR),
                    ),
                    # Focus Quest & Centered Ring Timer Card
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            "FOCUS QUEST",
                                            size=13,
                                            color=COLOR_ACCENT,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        self.timer_status_text,
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Row(
                                    [self.timer_minutes_field, self.timer_title_field],
                                    spacing=6,
                                ),
                                ft.Row(
                                    [
                                        ft.Container(
                                            self.ring, alignment=ft.alignment.center
                                        ),
                                        ft.Column(
                                            [
                                                self.timer_start_btn,
                                                self.timer_abort_btn,
                                            ],
                                            spacing=8,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=12,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER_COLOR),
                        expand=True,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
            expand=1,
        )

        # Root Layout: Two side-by-side columns that fit perfectly in standard screens
        self.page.add(
            ft.Row(
                [left_panel, right_panel],
                spacing=12,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

        self._refresh_profiles()

    # ------------------------------------------------------------------
    # Segmented timer ring (Geometrically centered text)
    # ------------------------------------------------------------------
    def _build_segmented_ring(self) -> ft.Stack:
        self.dots: list[ft.Container] = []
        radius = RING_DIAMETER / 2
        controls = []

        # Circular dots
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

        # Geometrically centered countdown text only
        controls.append(
            ft.Container(
                content=self.countdown_text,
                width=STACK_SIZE,
                height=STACK_SIZE,
                alignment=ft.alignment.center,
            )
        )

        return ft.Stack(controls, width=STACK_SIZE, height=STACK_SIZE)

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
                    color=COLOR_SUCCESS if completed else "#ffffff",
                    size=12,
                    expand=True,
                ),
                ft.Text(
                    f"+{quest.exp_reward} XP",
                    color=COLOR_ACTIVE,
                    size=11,
                ),
            ]

            if not completed:
                row_controls.append(
                    ft.ElevatedButton(
                        "Done",
                        height=28,
                        on_click=lambda e, q=quest: self._complete_quest(q),
                    )
                )

            rows.append(
                ft.Row(
                    row_controls,
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )

        self.quests_list.controls = rows or [
            ft.Text("No quests yet.", color="#64748b", size=12)
        ]
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
        _snack(self.page, f"Quest completed! +{quest.exp_reward} XP earned.")

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
            _snack(self.page, "Minutes must be a positive finite number.", ok=False)
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
        self.countdown_text.color = COLOR_SUCCESS
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
                f"✔ Floor {floor_no}: {room['info']} | {room['difficulty']} | +{reward} XP"
            )

        lines.append(f"— Run complete: {len(lines)} floors, +{total_exp} XP total —")
        self.dungeon_log.value = "\n".join(lines)

        self.player.add_exp(total_exp)
        StorageService.save_profile(self.player)
        self._refresh_hud()
        self.page.update()

        _snack(self.page, f"Dungeon cleared! +{total_exp} XP (+{XP_PER_FLOOR}/floor).")
