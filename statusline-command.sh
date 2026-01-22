#!/bin/bash

# Use --no-optional-locks to prevent index.lock issues
GIT="git --no-optional-locks"

# Git branch
branch=$($GIT branch --show-current 2>/dev/null)
if [ -z "$branch" ]; then
    branch_display="🚫 no git"
else
    branch_display="🌿 $branch"
fi

# Uncommitted files count (with --no-optional-locks to prevent locking)
uncommitted=$($GIT status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [ "$uncommitted" -eq 0 ]; then
    uncommitted_display="✨ clean"
else
    uncommitted_display="📝 $uncommitted changed"
fi

# Project directory (git root) and current location
git_root=$($GIT rev-parse --show-toplevel 2>/dev/null)

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
if $GIT rev-parse --abbrev-ref @{upstream} &>/dev/null; then
    ahead=$($GIT rev-list --count @{upstream}..HEAD 2>/dev/null || echo 0)
    behind=$($GIT rev-list --count HEAD..@{upstream} 2>/dev/null || echo 0)
    [ "$ahead" -gt 0 ] && ahead_behind="⬆$ahead "
    [ "$behind" -gt 0 ] && ahead_behind="${ahead_behind}⬇$behind"
fi

# Stash count
stash_count=$($GIT stash list 2>/dev/null | wc -l | tr -d ' ')
stash_display=""
[ "$stash_count" -gt 0 ] && stash_display="📦 $stash_count stashed"

# Time
time_display="🕐 $(date +%H:%M)"

# Language version detection with mismatch support
check_dir="${git_root:-$PWD}"
lang_display=""

# Helper to check if file exists in root or src/ subdirectory (monorepo pattern)
has_file() {
    [ -f "$check_dir/$1" ] || [ -f "$check_dir/src/$1" ]
}

# Get wanted version from .tool-versions (short: e.g., "1.16" from "1.16.2-otp-26")
get_wanted() {
    local tool="$1"
    grep "^$tool " "$check_dir/.tool-versions" 2>/dev/null | awk '{print $2}' | grep -oE '^[0-9]+\.[0-9]+'
}

# Get active version (short), returns empty if tool not available
get_active() {
    local tool="$1"
    case "$tool" in
        elixir) elixir --version 2>/dev/null | grep -oE 'Elixir [0-9]+\.[0-9]+' | cut -d' ' -f2 ;;
        python) python3 --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1 ;;
        ruby)   ruby --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1 ;;
        nodejs) node --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' ;;
        golang) go version 2>/dev/null | grep -oE 'go[0-9]+\.[0-9]+' | sed 's/go//' ;;
    esac
}

# Format version display: match=version, mismatch=want→have, missing=want ✗
format_version() {
    local icon="$1" tool="$2"
    local wanted=$(get_wanted "$tool")
    local active=$(get_active "$tool")

    if [ -n "$wanted" ]; then
        if [ -n "$active" ]; then
            if [ "$wanted" = "$active" ]; then
                echo "$icon $active"
            else
                echo "$icon $wanted→$active"
            fi
        else
            echo "$icon $wanted ✗"
        fi
    elif [ -n "$active" ]; then
        echo "$icon $active"
    fi
}

if has_file "mix.exs" || has_file "mix.lock"; then
    lang_display=$(format_version "💧" "elixir")
elif has_file "pyproject.toml" || has_file "requirements.txt" || has_file "setup.py"; then
    lang_display=$(format_version "🐍" "python")
elif has_file "Gemfile" || has_file ".ruby-version"; then
    lang_display=$(format_version "💎" "ruby")
elif has_file "package.json"; then
    lang_display=$(format_version "⬢" "nodejs")
elif has_file "go.mod"; then
    lang_display=$(format_version "🐹" "golang")
fi

# Build output - only include ahead_behind and stash if they have values
output="$branch_display"
[ -n "$ahead_behind" ] && output="$output $ahead_behind"
output="$output │ $uncommitted_display │ $dir_display │ 🧠 $model"
[ -n "$lang_display" ] && output="$output │ $lang_display"
[ -n "$stash_display" ] && output="$output │ $stash_display"
output="$output │ $time_display"

echo "$output"
