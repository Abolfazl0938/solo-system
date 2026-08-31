# main.py
from core.utils import get_system_status
from core.models import Player
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

    # 2. ساخت و تست مدل Player
    player = Player(name="Sung Jin-Woo")
    player.gain_exp(50)  # تست متد دریافت تجربه

    # 3. جدول استاتوس بازیکن
    table = Table(
        title="[bold yellow]⚡ PLAYER STATUS ⚡[/bold yellow]",
        border_style="bright_blue",
    )
    table.add_column("Attribute", style="bold cyan")
    table.add_column("Value", style="bold white")

    table.add_row("Name", player.name)
    table.add_row("Level", str(player.level))
    table.add_row("HP", f"{player.hp}/100")
    table.add_row("EXP", f"{player.exp}/100")

    console.print(table)


if __name__ == "__main__":
    display_dashboard()
