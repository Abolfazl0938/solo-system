"""Modern Dark-Themed GUI View for SoloSystem using Flet."""

from __future__ import annotations

import flet as ft
from core.models import Player, Quest, QuestStatus
from services.dungeon_service import generate_dungeon_run
from services.storage_service import StorageService
from services.time_service import TimeService


class SoloSystemApp:
    """Main Application View Controller managing UI state and services."""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.storage = StorageService()

        # Load initial profile
        profiles = self.storage.list_profiles()
        initial_name = profiles[0] if profiles else "Sung Jin-Woo"
        self.current_player: Player = self.storage.load_profile(initial_name)

        self._init_window()
        self._build_components()
        self._render()

    def _init_window(self) -> None:
        self.page.title = "SOLO SYSTEM // AWAKENED INTERFACE"
        self.page.bgcolor = "#0B0F19"
        self.page.padding = 24
        self.page.theme_mode = ft.ThemeMode.DARK

    def _build_components(self) -> None:
        # Header Info
        self.txt_title = ft.Text(
            "SYSTEM ACTIVE", size=22, weight=ft.FontWeight.BOLD, color="#38BDF8"
        )
        self.txt_system_time = ft.Text(
            TimeService.format_dual_timestamp(), size=12, color="#94A3B8"
        )

        # Profile Switcher
        self.dd_profiles = ft.Dropdown(
            label="Active Player Profile",
            width=230,
            dense=True,
            color="#FFFFFF",
        )
        self._refresh_profile_dropdown()
        self.dd_profiles.on_change = self._on_profile_switch

        # Player Stats
        self.txt_player_name = ft.Text(
            size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"
        )
        self.txt_rank = ft.Text(size=14, weight=ft.FontWeight.BOLD, color="#F59E0B")
        self.txt_level = ft.Text(size=14, color="#E2E8F0")
        self.pb_exp = ft.ProgressBar(
            value=0.0, color="#38BDF8", bgcolor="#1E293B", height=10
        )
        self.txt_exp = ft.Text(size=12, color="#94A3B8")

        # Layout Containers
        self.col_active_quests = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.col_archived_quests = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)

        self.tf_quest_title = ft.TextField(
            label="Quest Objective", expand=True, dense=True
        )
        self.tf_quest_exp = ft.TextField(label="EXP", value="50", width=90, dense=True)

        self.txt_dungeon_log = ft.Text(
            "Standing by for Dungeon Gate scan...\n",
            size=12,
            font_family="Consolas",
            color="#A7F3D0",
        )

    def _refresh_profile_dropdown(self) -> None:
        profiles = self.storage.list_profiles()
        self.dd_profiles.options = [ft.dropdown.Option(p) for p in profiles]
        self.dd_profiles.value = self.current_player.name

    def _refresh_state(self) -> None:
        p = self.current_player
        self.txt_player_name.value = p.name.upper()
        self.txt_rank.value = f"RANK: {p.rank}"
        self.txt_level.value = f"LVL: {p.level}"

        req_exp = p.exp_to_next_level
        progress = min(p.exp / req_exp, 1.0) if req_exp > 0 else 0.0
        self.pb_exp.value = progress
        self.txt_exp.value = f"EXP: {p.exp} / {req_exp} ({int(progress * 100)}%)"

        # Active Quests
        self.col_active_quests.controls.clear()
        active_quests = [q for q in p.quests if q.status == QuestStatus.PENDING]
        if not active_quests:
            self.col_active_quests.controls.append(
                ft.Text("No active quests remaining.", color="#64748B", size=13)
            )
        else:
            for q in active_quests:
                self.col_active_quests.controls.append(self._build_quest_card(q))

        # History
        self.col_archived_quests.controls.clear()
        history = [q for q in p.quests if q.status != QuestStatus.PENDING]
        for q in reversed(history[-6:]):
            color = "#10B981" if q.status == QuestStatus.COMPLETED else "#EF4444"
            self.col_archived_quests.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(q.title, size=12, expand=True),
                            ft.Text(f"[{q.status.value}]", color=color),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=6,
                    bgcolor="#0F172A",
                    border_radius=4,
                )
            )
        self.txt_system_time.value = TimeService.format_dual_timestamp()
        self.page.update()

    def _build_quest_card(self, quest: Quest) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(quest.title, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{quest.exp_reward} EXP", size=11),
                        ],
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        "Complete",
                        bgcolor="#059669",
                        color="white",
                        on_click=lambda _: self._complete_quest(quest),
                    ),
                    ft.ElevatedButton(
                        "Fail",
                        bgcolor="#DC2626",
                        color="white",
                        on_click=lambda _: self._fail_quest(quest),
                    ),
                ]
            ),
            bgcolor="#1E293B",
            padding=12,
            border_radius=8,
        )

    def _render(self) -> None:
        header = ft.Container(
            content=ft.Row(
                [ft.Column([self.txt_title, self.txt_system_time]), self.dd_profiles],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
        )

        stats_card = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [self.txt_player_name, self.txt_rank, self.txt_level],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.pb_exp,
                    self.txt_exp,
                ]
            ),
            bgcolor="#1E293B",
            padding=16,
            border_radius=8,
        )

        quest_form = ft.Container(
            content=ft.Column(
                [
                    ft.Text("ISSUE NEW QUEST", size=12, color="#94A3B8"),
                    ft.Row(
                        [
                            self.tf_quest_title,
                            self.tf_quest_exp,
                            ft.ElevatedButton(
                                "Add", bgcolor="#2563EB", on_click=self._on_add_quest
                            ),
                        ]
                    ),
                ]
            ),
            bgcolor="#111827",
            padding=14,
            border_radius=8,
        )

        dungeon_box = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("DUNGEON GATE TERMINAL", size=12, color="#38BDF8"),
                            ft.ElevatedButton(
                                "Enter Gate",
                                bgcolor="#7C3AED",
                                on_click=self._on_enter_dungeon,
                            ),
                        ]
                    ),
                    ft.Container(
                        content=self.txt_dungeon_log,
                        bgcolor="#030712",
                        padding=10,
                        border_radius=6,
                        height=110,
                    ),
                ]
            ),
            bgcolor="#111827",
            padding=14,
            border_radius=8,
        )

        self.page.add(
            header,
            ft.Row(
                [
                    ft.Column(
                        [stats_card, quest_form, self.col_active_quests], expand=2
                    ),
                    ft.Column([dungeon_box, self.col_archived_quests], expand=1),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )
        self._refresh_state()

    def _on_profile_switch(self, e) -> None:
        self.current_player = self.storage.load_profile(self.dd_profiles.value)
        self._refresh_state()

    def _on_add_quest(self, e) -> None:
        if self.tf_quest_title.value:
            new_quest = Quest(
                title=self.tf_quest_title.value,
                exp_reward=int(self.tf_quest_exp.value or 0),
            )
            self.current_player.quests.append(new_quest)
            self.storage.save_profile(self.current_player)
            self._refresh_state()

    def _complete_quest(self, quest: Quest) -> None:
        quest.complete()
        self.current_player.add_exp(quest.exp_reward)
        self.storage.save_profile(self.current_player)
        self._refresh_state()

    def _fail_quest(self, quest: Quest) -> None:
        quest.status = QuestStatus.FAILED
        quest.completed_at = TimeService.get_current_timestamps()
        self.storage.save_profile(self.current_player)
        self._refresh_state()

    def _on_enter_dungeon(self, e) -> None:
        self.txt_dungeon_log.value = "[GATE DETECTED] Scanning...\n"
        self.page.update()
        total_exp = 0
        log = []
        for room in generate_dungeon_run(3):
            gained = (room["floor"]) * 30
            total_exp += gained
            log.append(f"• {room['info']} ({room['difficulty']}) -> +{gained} EXP")

        self.current_player.add_exp(total_exp)
        self.storage.save_profile(self.current_player)
        log.append(f"\n[CLEARED] Total: +{total_exp} EXP!")
        self.txt_dungeon_log.value = "\n".join(log)
        self._refresh_state()
