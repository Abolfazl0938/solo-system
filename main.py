from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt

from core.models import Player, Quest, QuestNotFoundError
from services.storage import StorageService

console = Console()


def display_quests_table(player: Player) -> None:
    """Render player quests inside a clean terminal table."""
    if not player.quests:
        console.print("[yellow]No quests found in the quest log![/yellow]")
        return

    table = Table(title="📜 DAILY QUEST LOG", show_lines=True)
    table.add_column("Quest ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Reward (EXP)", justify="center", style="green")
    table.add_column("Status", justify="center")

    for q in player.quests:
        status_text = (
            "[bold green]COMPLETED[/bold green]"
            if q.status.value == "COMPLETED"
            else "[bold yellow]PENDING[/bold yellow]"
        )
        table.add_row(str(q.id), q.title, f"+{q.reward_exp} EXP", status_text)

    console.print(table)


def main() -> None:
    storage = StorageService()
    data = storage.load_player_data()

    console.print(
        Panel.fit(
            "[bold magenta]⚡ SOLO SYSTEM CORE INITIALIZING ⚡[/bold magenta]",
            border_style="magenta",
        )
    )

    # 1. Loading / Initialization Phase
    if data is not None:
        player = Player.from_dict(data)
        console.print(
            f"[bold green]✔ Welcome back, Hunter {player.name}![/bold green]\n"
        )
    else:
        name = Prompt.ask("[bold cyan]Enter new hunter name[/bold cyan]")
        player = Player(name=name)
        console.print(
            f"[bold green]✔ New hunter profile initialized for {name}.[/bold green]\n"
        )

    # 2. Game Loop Phase
    while True:
        console.print(
            "\n[dim]Available commands: [cyan]status[/cyan] | [cyan]add[/cyan] | [cyan]list[/cyan] | [cyan]complete[/cyan] | [red]exit[/red][/dim]"
        )
        command = Prompt.ask("[bold yellow]SYSTEM[/bold yellow] >>").strip().lower()

        if command == "exit":
            console.print("[bold red]Shutting down system...[/bold red]")
            break

        elif command == "status":
            console.print(
                Panel(
                    str(player),
                    title=f"👤 Hunter Profile: {player.name}",
                    border_style="cyan",
                )
            )

        elif command == "add":
            quest_id = IntPrompt.ask("[cyan]Enter Quest ID[/cyan]")
            quest_title = Prompt.ask("[cyan]Enter Quest Title[/cyan]")
            quest_reward_exp = IntPrompt.ask("[cyan]Enter Reward EXP[/cyan]")

            new_quest = Quest(
                id=quest_id, title=quest_title, reward_exp=quest_reward_exp
            )
            player.add_quest(new_quest)
            console.print(
                f"[bold green]✔ Quest '{quest_title}' registered successfully.[/bold green]"
            )

        elif command == "list":
            display_quests_table(player)

        elif command == "complete":
            quest_id = IntPrompt.ask("[cyan]Enter target Quest ID to complete[/cyan]")
            try:
                player.complete_quest(quest_id)
                console.print(
                    f"[bold green]🎉 Quest #{quest_id} completed! EXP rewarded.[/bold green]"
                )
            except QuestNotFoundError as e:
                console.print(f"[bold red]❌ Error: {e}[/bold red]")

        else:
            console.print("[bold red]Unknown command! Please try again.[/bold red]")

    # 3. Teardown & Persistence Phase
    storage.save_player(player)
    console.print(
        "[bold green]💾 System data saved successfully. Farewell, Hunter![/bold green]"
    )


if __name__ == "__main__":
    main()
