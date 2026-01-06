# Claude Scripts

Utility scripts for managing the _apps workspace.

## Setup

```bash
cd ~/_apps/.claude/scripts
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Scripts

### sync-repos.py

Syncs all `app-*` repositories from the surgeventures GitHub org to `_apps`.

**Run it:**
```bash
./sync-repos.py
```

**What it does:**
- Clones new `app-*` repos
- Pulls latest changes for existing repos
- Shows status for each repo

**Requirements:**
- `gh` CLI authenticated (`gh auth login`)

**Configuration:**
Edit these variables in the script if needed:
- `ORG` - GitHub org (default: `surgeventures`)
- `REPO_PREFIX` - Repo name prefix (default: `app-`)
