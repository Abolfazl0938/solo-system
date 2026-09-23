import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from core.models import Player, Quest
from core.context_managers import DungeonRaidSession, quest_transaction
from services.dungeon_service import generate_dungeon_run
from services.network_service import NetworkService
from services.storage_service import StorageService

console = Console()
storage = StorageService()


def get_or_create_player() -> Player:
    """Load player from disk or initialize a new hunter profile."""
    saved_player = storage.load_player()
    if saved_player:
        console.print(
            f"[bold green]✔ Loaded profile for Hunter '{saved_player.name}' from storage![/]"
        )
        return saved_player

    console.print(Panel.fit("[bold cyan]SoloSystem - Hunter Awakening[/]"))
    name = Prompt.ask("[yellow]Enter Hunter Name[/]", default="Sung Jin-Woo")
    player = Player(name=name, rank="E")
    storage.save_player(player)
    return player


def display_status(player: Player) -> None:
    table = Table(title=f"Hunter Status: {player.name}", style="bold magenta")
    table.add_column("Attribute", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Level", str(player.level))
    table.add_row("EXP", f"{player.exp} / {player.level * 100}")
    table.add_row("Rank", player.rank)
    table.add_row("Active Quests", str(len(player)))
    console.print(table)


def display_quests(player: Player) -> None:
    if len(player) == 0:
        console.print("[yellow]No active quests found.[/]")
        return

    table = Table(title="Daily Quest Log", style="bold blue")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Description")
    table.add_column("EXP Reward")
    table.add_column("Rank")
    table.add_column("Status")

    for q in player:
        status = "[green]COMPLETED[/]" if q.is_completed else "[red]PENDING[/]"
        table.add_row(
            str(q.id), q.title, q.description, str(q.reward_exp), q.rank, status
        )

    console.print(table)


def add_daily_quests(player: Player) -> None:
    quests_to_add = [
        Quest(
            id=1, title="Push-ups", description="100 Push-ups", reward_exp=100, rank="E"
        ),
        Quest(
            id=2, title="Sit-ups", description="100 Sit-ups", reward_exp=100, rank="E"
        ),
        Quest(id=3, title="Running", description="10km Run", reward_exp=150, rank="E"),
    ]

    with quest_transaction(player):
        for q in quests_to_add:
            if q not in player:
                player.add_quest(q)

    storage.save_player(player)
    console.print("[bold green]✔ Daily quests assigned and saved to disk.[/]")


def run_dungeon(player: Player) -> None:
    console.print("[bold red]⚡ Entering Dungeon Raid...[/]")
    with DungeonRaidSession("Dungeon Rank E") as session:
        for floor_data in generate_dungeon_run(max_floors=3):
            console.print(
                f"  [cyan]» {floor_data['info']}[/] | Difficulty: {floor_data['difficulty']}"
            )
            player.gain_exp(50)
            session.record_defeat()

    storage.save_player(player)
    console.print("[bold green]✔ Dungeon cleared! EXP awarded and progress saved.[/]")


async def scan_gates() -> None:
    network = NetworkService()
    gates = [
        {"id": "G-101", "rank": "E"},
        {"id": "G-102", "rank": "D"},
        {"id": "G-103", "rank": "B"},
    ]
    console.print("[bold cyan]🌐 Scanning network gates concurrently via AsyncIO...[/]")
    results = await network.scan_all_gates(gates)
    for res in results:
        console.print(f"  [green]✔ {res['status']}[/]")


def main() -> None:
    player = get_or_create_player()

    while True:
        console.print("\n" + "=" * 45)
        console.print("[bold cyan]SOLO SYSTEM INTERFACE[/]")
        console.print("1. View Hunter Status")
        console.print("2. View Quest Log")
        console.print("3. Accept Daily Quests (Atomic Transaction)")
        console.print("4. Enter Dungeon (Generator & Context Session)")
        console.print("5. Scan Active Gates (AsyncIO Network)")
        console.print("6. Save Progress")
        console.print("0. Exit")
        console.print("=" * 45)

        choice = Prompt.ask(
            "Select an option", choices=["0", "1", "2", "3", "4", "5", "6"]
        )

        if choice == "1":
            display_status(player)
        elif choice == "2":
            display_quests(player)
        elif choice == "3":
            add_daily_quests(player)
        elif choice == "4":
            run_dungeon(player)
        elif choice == "5":
            asyncio.run(scan_gates())
        elif choice == "6":
            if storage.save_player(player):
                console.print("[bold green]✔ Game state saved successfully.[/]")
        elif choice == "0":
            storage.save_player(player)
            console.print("[bold yellow]Saving game state... Exiting Solo System.[/]")
            break


if __name__ == "__main__":
    main()
