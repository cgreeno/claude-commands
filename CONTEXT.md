# Fresha CTO Workspace Context

This workspace (`~/_apps/`) contains tooling and scripts for managing CTO responsibilities at Fresha.

## Project Monitoring

- **223 project channels** in Slack (you're a member of 151)
- Project channels follow naming patterns: `proj_*` or `proj-*`
- Channel data stored in `~/_apps/.claude/command_resources/projects_to_monitor.md`

## Slash Commands

Available commands for CTO work:
- `/cto:list-proj-channels` - Discover and sync all project channels from Slack
- `/cto:check-projects [days]` - Extract and analyze project updates from channels

## Directory Structure

```
~/_apps/
├── .claude/
│   ├── commands/          # Slash command definitions
│   ├── command_resources/ # Data files (projects_to_monitor.md, etc.)
│   ├── scripts/           # Python scripts that support slash commands
│   └── tmp_output/        # Script outputs and temporary data
└── [your code projects]
```

## Notes

This is your CTO workspace - use this for:
- Monitoring project channels
- Generating updates and reports
- Tracking communications with CEO and team
- Project-related tooling and automation
