# main.py
from core.utils import get_system_status
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def display_welcome():
    status = get_system_status()

    content = Text()
    content.append("● System: ", style="bold cyan")
    content.append(f"{status['system_name']}\n", style="bold white")
    content.append("● Version: ", style="bold cyan")
    content.append(f"{status['version']}\n", style="bold green")
    content.append("● Status: ", style="bold cyan")
    content.append(f"{status['status']}", style="bold yellow")

    panel = Panel(
        content,
        title="[bold red]⚡ SYSTEM INITIALIZED ⚡[/bold red]",
        border_style="bright_blue",
        padding=(1, 2),
    )
    console.print(panel)


if __name__ == "__main__":
    display_welcome()
