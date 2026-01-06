#!/bin/bash

# Git branch
branch=$(git branch --show-current 2>/dev/null)
if [ -z "$branch" ]; then
    branch_display="🚫 no git"
else
    branch_display="🌿 $branch"
fi

# Uncommitted files count
uncommitted=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [ "$uncommitted" -eq 0 ]; then
    uncommitted_display="✨ clean"
else
    uncommitted_display="📝 $uncommitted changed"
fi

# Project directory (git root) and current location
git_root=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -n "$git_root" ]; then
    project=$(basename "$git_root")
    if [ "$PWD" != "$git_root" ]; then
        subdir=$(echo "$PWD" | sed "s|$git_root/||")
        dir_display="📁 $project/$subdir"
    else
        dir_display="📁 $project"
    fi
else
    # Not in a git repo - show current directory
    dir_display="📁 $(basename "$PWD")"
fi

# Model
model="${CLAUDE_MODEL:-opus}"

# Ahead/behind remote
ahead_behind=""
if git rev-parse --abbrev-ref @{upstream} &>/dev/null; then
    ahead=$(git rev-list --count @{upstream}..HEAD 2>/dev/null || echo 0)
    behind=$(git rev-list --count HEAD..@{upstream} 2>/dev/null || echo 0)
    [ "$ahead" -gt 0 ] && ahead_behind="⬆$ahead "
    [ "$behind" -gt 0 ] && ahead_behind="${ahead_behind}⬇$behind"
fi

# Stash count
stash_count=$(git stash list 2>/dev/null | wc -l | tr -d ' ')
stash_display=""
[ "$stash_count" -gt 0 ] && stash_display="📦 $stash_count stashed"

# Time
time_display="🕐 $(date +%H:%M)"

# Build output - only include ahead_behind and stash if they have values
output="$branch_display"
[ -n "$ahead_behind" ] && output="$output $ahead_behind"
output="$output │ $uncommitted_display │ $dir_display │ 🧠 $model"
[ -n "$stash_display" ] && output="$output │ $stash_display"
output="$output │ $time_display"

echo "$output"
