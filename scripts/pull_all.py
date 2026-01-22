#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich>=13.0.0"]
# ///
"""Pull all git repos in ~/_apps directory with progress display."""

import subprocess
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


def find_git_repos(base_path: Path) -> list[Path]:
    """Find all directories containing a .git folder."""
    return sorted(p.parent for p in base_path.glob("*/.git") if p.is_dir())


def git_pull(repo_path: Path) -> tuple[bool, str]:
    """Run git pull in a repo, return (success, output)."""
    result = subprocess.run(
        ["git", "pull"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip() or result.stderr.strip()
    return result.returncode == 0, output


def main():
    base_path = Path.home() / "_apps"

    if not base_path.exists():
        console.print(f"[red]Directory not found: {base_path}[/red]")
        return

    repos = find_git_repos(base_path)

    if not repos:
        console.print("[yellow]No git repositories found.[/yellow]")
        return

    console.print(f"Found [cyan]{len(repos)}[/cyan] repositories\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Pulling repos...", total=len(repos))

        for repo in repos:
            progress.update(task, description=f"Pulling [cyan]{repo.name}[/cyan]")
            success, output = git_pull(repo)

            if success:
                if "Already up to date" in output:
                    console.print(f"  [dim]{repo.name}: up to date[/dim]")
                else:
                    console.print(f"  [green]{repo.name}: {output}[/green]")
            else:
                console.print(f"  [red]{repo.name}: {output}[/red]")

            progress.advance(task)

    console.print("\n[green]Done![/green]")


if __name__ == "__main__":
    main()
