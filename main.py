import asyncio
import os
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

# افزودن مسیر ریشه پروژه
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import Player, Quest, QuestStatus
from core.context_managers import DungeonRaidSession, quest_transaction
from services.dungeon_service import generate_dungeon_run
from services.network_service import NetworkService

console = Console()


def display_status(player: Player) -> None:
    """نمایش پنل مشخصات بازیکن با فرمت‌بندی مدرن"""
    info = (
        f"[bold cyan]Name:[/bold cyan] {player.name}  |  "
        f"[bold yellow]Rank:[/bold yellow] {player.rank.name}  |  "
        f"[bold green]Level:[/bold green] {player.level}  |  "
        f"[bold magenta]EXP:[/bold magenta] {player.exp}/100"
    )
    console.print(
        Panel(info, title="[bold blue]HUNTER STATUS[/bold blue]", border_style="cyan")
    )


def display_quests(player: Player) -> None:
    """نمایش جدول کوئست‌ها با استفاده از پروتکل کانتینر Player"""
    table = Table(
        title="[bold green]ACTIVE QUESTS LOG[/bold green]", border_style="bright_blue"
    )
    table.add_column("Index", style="dim", justify="center")
    table.add_column("ID", style="bold yellow")
    table.add_column("Title", style="white")
    table.add_column("Status", justify="center")
    table.add_column("Reward (EXP)", justify="right", style="cyan")

    if len(player) == 0:
        table.add_row("-", "-", "No active quests registered.", "-", "-")
    else:
        for idx, quest in enumerate(player):
            status_color = (
                "green" if quest.status == QuestStatus.COMPLETED else "yellow"
            )
            table.add_row(
                str(idx),
                quest.id,
                quest.title,
                f"[{status_color}]{quest.status.value}[/{status_color}]",
                f"+{quest.exp_reward}",
            )

    console.print(table)


async def run_gate_scan() -> None:
    """اجرای اسکن ناهمگام گیت‌ها"""
    console.print("[bold yellow]Connecting to Satellite Gate Radar...[/bold yellow]")
    gates = ["Gate-Alpha", "Gate-Red", "Gate-Omega", "Gate-Shadow"]

    start = time.perf_counter()
    results = await NetworkService.scan_all_gates(gates)
    elapsed = time.perf_counter() - start

    table = Table(title="[bold red]RADAR SCAN RESULTS[/bold red]", border_style="red")
    table.add_column("Gate ID", style="bold white")
    table.add_column("Status", justify="center")
    table.add_column("Danger Rank", justify="center", style="bold red")
    table.add_column("Ping", justify="right", style="dim")

    for res in results:
        table.add_row(
            res["gate_id"], res["status"], res["danger_level"], res["response_time"]
        )

    console.print(table)
    console.print(f"[dim]All scans completed in {elapsed:.2f}s concurrently.[/dim]\n")


def simulate_dungeon_raid(player: Player) -> None:
    """شبیه‌سازی دانجن با کانتکست منیجر و ارزیابی تنبل طبقات"""
    dungeon_name = "Demon Castle"
    console.print(
        f"\n[bold magenta]Preparing raid team for {dungeon_name}...[/bold magenta]"
    )

    with DungeonRaidSession(player, dungeon_name) as session:
        for floor_data in generate_dungeon_run(floor_count=3):
            console.print(
                f" -> Clearing [bold yellow]{floor_data['floor']}[/bold yellow] | Monster: {floor_data['monster']} | EXP: +{floor_data['exp']}"
            )
            time.sleep(0.3)
        session.mark_cleared()
        player.gain_exp(120)


def add_quest_safely(player: Player) -> None:
    """افزودن کوئست جدید در قالب تراکنش اتمیک با Rollback"""
    quest_id = f"q{len(player) + 1}"
    title = Prompt.ask("[cyan]Enter quest title[/cyan]")
    exp = int(Prompt.ask("[cyan]Enter EXP reward[/cyan]", default="50"))

    try:
        with quest_transaction(player):
            new_quest = Quest(
                id=quest_id,
                title=title,
                description=f"Task: {title}",
                exp_reward=exp,
                status=QuestStatus.PENDING,
            )
            player.add_quest(new_quest)
            console.print(
                "[bold green]✔ Quest committed to system memory successfully![/bold green]"
            )
    except Exception as err:
        console.print(f"[bold red]✘ Transaction aborted:[/bold red] {err}")


async def main_loop() -> None:
    # ساخت پلیر اولیه
    player = Player(name="Sung Jin-Woo", level=1)

    # همگام‌سازی اولیه از طریق سرور ناهمگام
    await NetworkService.sync_player_data(player)

    # کوئست‌های پیش‌فرض اولیه
    player.add_quest(
        Quest("q1", "Daily Push-ups", "Do 100 pushups", 40, QuestStatus.COMPLETED)
    )
    player.add_quest(Quest("q2", "Daily Run", "Run 10km", 60, QuestStatus.PENDING))

    while True:
        console.clear()
        display_status(player)
        display_quests(player)

        console.print("\n[bold]SYSTEM MENU:[/bold]")
        console.print("1. [cyan]Add New Quest (Atomic Transaction)[/cyan]")
        console.print(
            "2. [magenta]Raid Dungeon (Generator + Context Manager)[/magenta]"
        )
        console.print("3. [yellow]Scan Gates Radar (Async/Await Concurrent)[/yellow]")
        console.print("4. [red]Exit System[/red]")

        choice = Prompt.ask(
            "\n[bold green]Select an option[/bold green]",
            choices=["1", "2", "3", "4"],
            default="4",
        )

        if choice == "1":
            add_quest_safely(player)
            Prompt.ask("\nPress Enter to continue...")
        elif choice == "2":
            simulate_dungeon_raid(player)
            Prompt.ask("\nPress Enter to continue...")
        elif choice == "3":
            await run_gate_scan()
            Prompt.ask("\nPress Enter to continue...")
        elif choice == "4":
            console.print(
                "[bold cyan]System entering sleep mode. Goodbye, Hunter.[/bold cyan]"
            )
            break


if __name__ == "__main__":
    asyncio.run(main_loop())
