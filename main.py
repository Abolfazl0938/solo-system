# main.py
from core.utils import get_system_status
from core.models import Player, Quest, QuestNotFoundError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def display_dashboard():
    # 1. وضعیت سیستم
    status = get_system_status()
    console.print(
        f"[bold cyan]● System:[/bold cyan] {status['system_name']} | [bold green]v{status['version']}[/bold green]\n"
    )

    # 2. ساخت بازیکن و کوئیست‌ها
    player = Player(name="Sung Jin-Woo")

    quest1 = Quest(id=1, title="100 Push-ups", reward_exp=50)
    quest2 = Quest(id=2, title="10km Run", reward_exp=100)

    player.add_quest(quest1)
    player.add_quest(quest2)

    # تکمیل مأموریت اول
    player.complete_quest(quest_id=1)
    try:
        player.complete_quest(quest_id=100)
    except QuestNotFoundError as e:
        console.print(f"[bold red]⚠ Quest Error:[/bold red] {e}")

    # 3. جدول مشخصات بازیکن
    p_table = Table(
        title="[bold yellow]⚡ PLAYER STATUS ⚡[/bold yellow]",
        border_style="bright_blue",
    )
    p_table.add_column("Attribute", style="bold cyan")
    p_table.add_column("Value", style="bold white")
    p_table.add_row("Name", player.name)
    p_table.add_row("Level", str(player.level))
    p_table.add_row("HP", f"{player.hp}/100")
    p_table.add_row("EXP", f"{player.exp}/100")
    console.print(p_table)

    console.print("\n")

    # 4. جدول کوئیست‌ها
    q_table = Table(
        title="[bold magenta]📋 DAILY QUESTS 📋[/bold magenta]",
        border_style="bright_magenta",
    )
    q_table.add_column("ID", style="bold cyan")
    q_table.add_column("Title", style="bold white")
    q_table.add_column("Reward", style="bold yellow")
    q_table.add_column("Status", style="bold green")

    for q in player.quests:
        status_color = "green" if q.status.value == "COMPLETED" else "yellow"
        q_table.add_row(
            str(q.id),
            q.title,
            f"{q.reward_exp} EXP",
            f"[{status_color}]{q.status.value}[/{status_color}]",
        )
    console.print(q_table)


if __name__ == "__main__":
    display_dashboard()
