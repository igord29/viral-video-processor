"""Display utilities using Rich for beautiful CLI output."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich import print as rprint

console = Console()


def print_header(text: str):
    """Print a formatted header."""
    console.print(f"\n[bold cyan]{text}[/bold cyan]\n")


def print_success(text: str):
    """Print a success message."""
    console.print(f"[green]✓[/green] {text}")


def print_error(text: str):
    """Print an error message."""
    console.print(f"[red]✗[/red] {text}")


def print_warning(text: str):
    """Print a warning message."""
    console.print(f"[yellow]⚠[/yellow] {text}")


def print_info(text: str):
    """Print an info message."""
    console.print(f"[blue]ℹ[/blue] {text}")


def confirm_action(prompt: str) -> bool:
    """Ask user to confirm an action."""
    return Confirm.ask(f"[yellow]{prompt}[/yellow]")


def get_user_input(prompt: str, default: str = None) -> str:
    """Get user input with a prompt."""
    return Prompt.ask(f"[cyan]{prompt}[/cyan]", default=default)


def display_video_info(info: dict):
    """Display video information in a formatted panel."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Title", info.get('title', 'N/A'))
    table.add_row("Channel", info.get('channel', 'N/A'))
    table.add_row("Duration", format_duration(info.get('duration', 0)))
    table.add_row("Views", f"{info.get('view_count', 0):,}")
    table.add_row("Likes", f"{info.get('like_count', 0):,}")

    if info.get('upload_date'):
        table.add_row("Upload Date", info['upload_date'])

    table.add_row("URL", info.get('webpage_url', 'N/A'))

    panel = Panel(table, title="[bold]Video Information[/bold]", border_style="blue")
    console.print(panel)


def display_clip_candidates(clips: list):
    """Display clip candidates with their scores."""
    table = Table(title="[bold]Top Clip Candidates[/bold]", show_lines=True)

    table.add_column("#", style="cyan", width=4)
    table.add_column("Time", style="green", width=15)
    table.add_column("Duration", style="yellow", width=10)
    table.add_column("Score", style="magenta", width=8)
    table.add_column("Reason", style="white")

    for i, clip in enumerate(clips, 1):
        score_color = "green" if clip['score'] >= 8 else "yellow" if clip['score'] >= 6 else "white"
        table.add_row(
            str(i),
            f"{format_time(clip['start_time'])} - {format_time(clip['end_time'])}",
            f"{clip['duration']:.1f}s",
            f"[{score_color}]{clip['score']:.1f}/10[/{score_color}]",
            clip.get('reason', '')[:60] + ("..." if len(clip.get('reason', '')) > 60 else "")
        )

    console.print(table)


def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS or MM:SS."""
    if seconds < 0:
        return "N/A"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_time(seconds: float) -> str:
    """Format time in seconds to MM:SS.mmm."""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:05.2f}"


def get_progress_context():
    """Get a Rich progress context manager."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    )
