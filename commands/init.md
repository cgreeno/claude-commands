---
description: Initialize project for focused work - sets up branch, CLAUDE.md, and plan
---

Initialize this project for a new task. Follow these steps in order:

## Step 1: Ask for the goal

Ask me: "What do you want to accomplish?"

Wait for my response before continuing.

## Step 2: Detect project language

Check for these files to determine the primary language:
- `mix.exs` → Elixir (use `@~/.claude/standards/elixir.md`)
- `package.json` → TypeScript (use `@~/.claude/standards/typescript.md`)
- `pyproject.toml` or `requirements.txt` → Python (use `@~/.claude/standards/python.md`)
- `go.mod` → Go (use `@~/.claude/standards/go.md`)

If multiple found, ask which is primary. If none found, ask what language we're working in.

## Step 3: Handle branching

Check the current branch:

**If on main:**
1. Run `git pull origin main`
2. Generate branch name from goal (lowercase, hyphens, e.g., "add-user-auth")
3. Create and checkout new branch

**If on a feature branch:**
1. Run `git fetch origin main`
2. Check for PR: `gh pr view --json state,url`

   - **PR exists and merged**: Tell me "This branch's PR was merged. Creating new branch from main." Then checkout main, pull, and create new branch from goal.

   - **PR exists and NOT merged**: Show me the PR URL and ask: "This branch has an open PR: [url]. What changes do you want to make?"

   - **No PR**: Ask me: "You're on branch [name] with no PR. Continue here or create new branch from main?"

## Step 4: Set up CLAUDE.md

Check if CLAUDE.md exists in project root:

**If exists**: Ask me: "Project already has CLAUDE.md. Overwrite with global template or keep existing?"

**If not exists or I choose overwrite**:
1. Copy `~/.claude/CLAUDE.md` to project root
2. Append the language-specific reference based on Step 2:
```markdown

## Language Standards
@~/.claude/standards/[language].md
```

## Step 5: Create plan.md

Create `plan.md` in project root with:

```markdown
# Plan: [Goal from Step 1]

## Objective
[Restate goal clearly]

## Tasks
- [ ] Explore codebase to understand current implementation
- [ ] [Additional tasks based on goal]

## Notes
- Language: [detected language]
- Branch: [current branch name]
```

## Step 6: Explore and enter plan mode

1. Look for README.md in the current directory
   - If found, read it to understand the project
   - If not found, look one level up (`../README.md`), then two levels up (`../../README.md`)
   - Read the first README.md you find

2. Explore the codebase structure to understand the project layout

3. Tell me: "Ready to plan. Here's what I understand about this project: [brief summary from README/exploration]. Let me create a detailed plan for: [goal]"

4. Enter plan mode and create a detailed implementation plan based on the goal and what you learned.
