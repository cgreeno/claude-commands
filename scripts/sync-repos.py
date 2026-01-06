#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich>=13.0.0"]
# ///
"""Sync all app-* repos from GitHub to _apps directory.

Run from anywhere: ~/.claude/scripts/sync-repos.py
Or add an alias: alias sync-repos='~/.claude/scripts/sync-repos.py'
"""

import subprocess
from pathlib import Path
from rich.console import Console
from rich.progress import Progress

console = Console()

# Configuration
ORG = "surgeventures"  # Change this to your GitHub org or username
REPO_PREFIX = "app-"
APPS_DIR = Path.home() / "_apps"


def get_app_repos() -> list[str]:
    """Fetch all repos matching the prefix from GitHub."""
    result = subprocess.run(
        ["gh", "repo", "list", ORG, "--limit", "1000", "--json", "name", "--jq", f".[] | select(.name | startswith(\"{REPO_PREFIX}\")) | .name"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [name.strip() for name in result.stdout.strip().split("\n") if name.strip()]


def sync_repo(repo_name: str) -> tuple[str, bool]:
    """Clone or pull a single repo. Returns (status_message, success)."""
    repo_path = APPS_DIR / repo_name
    repo_url = f"{ORG}/{repo_name}"

    if repo_path.exists():
        try:
            # Use --rebase --autostash to handle local changes gracefully
            subprocess.run(
                ["git", "-C", str(repo_path), "pull", "--rebase", "--autostash"],
                capture_output=True,
                text=True,
                check=True,
            )
            return (f"✓ Updated {repo_name}", True)
        except subprocess.CalledProcessError as e:
            return (f"✗ Failed to update {repo_name}: {e.stderr}", False)
    else:
        try:
            subprocess.run(
                ["gh", "repo", "clone", repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            return (f"✓ Cloned {repo_name}", True)
        except subprocess.CalledProcessError as e:
            return (f"✗ Failed to clone {repo_name}: {e.stderr}", False)


def main() -> None:
    """Sync all app-* repositories."""
    console.print(f"[bold blue]Fetching {REPO_PREFIX}* repos from {ORG}...[/bold blue]")

    repos = get_app_repos()

    if not repos:
        console.print(f"[yellow]No repos found matching '{REPO_PREFIX}*'[/yellow]")
        return

    console.print(f"[green]Found {len(repos)} repos[/green]\n")

    success_count = 0

    with Progress() as progress:
        task = progress.add_task("[cyan]Syncing repos...", total=len(repos))

        for repo in repos:
            message, success = sync_repo(repo)
            console.print(message)
            if success:
                success_count += 1
            progress.advance(task)

    console.print(f"\n[bold green]Done! {success_count}/{len(repos)} repos synced successfully[/bold green]")


if __name__ == "__main__":
    main()
