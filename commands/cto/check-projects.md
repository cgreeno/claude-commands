---
description: Extract and analyze project updates from Slack channels
argument-hint: [days]
---

Extract structured project updates from monitored Slack channels and enrich with Notion data.

**Date Range:** $1 (e.g., "7d" for last 7 days, "30d" for last 30 days)

If no date range provided, ask the user: "How many days back should I look? (e.g., 7d, 30d, 60d)"

---

## Step 1: Read Project List and Filter by Membership

1. Read `~/.claude/command_resources/projects_to_monitor.md`
2. Extract ONLY channels where **Your Membership: ✅ Member** is present
3. Ignore all channels where **Your Membership: ❌ Not a member**
4. This ensures you only monitor projects where you have visibility

---

## Step 2: Extract Updates from Slack

For each project channel in the monitoring list:

**Look for messages matching this pattern:**
```
Feature: [Feature Name]
Status: [Status] [emoji]
Health: [Health Status] [emoji]
Release date: [Date] ([percentage]%)
```

**Instructions:**
1. Use Slack MCP `get_channel_history` to fetch messages from the past [X] days
2. Parse each message to find ones matching the update pattern above
3. Extract:
   - Feature name
   - Status (e.g., "In development", "Planning", "Testing")
   - Health (e.g., "On track", "At risk", "Blocked")
   - Health indicator (emoji: 🟢 green = healthy, 🟡 yellow = warning, 🔴 red = critical)
   - Release date
   - Completion percentage (if present)
   - Full message text (for summary)
   - Message author
   - Message timestamp
   - Slack message link/permalink

4. Store ALL matching updates (don't filter to just latest - keep history)

---

## Step 3: Enrich with Notion Data

For each project that has updates:

1. Search Notion Product Roadmap database for matching projects:
   - Try exact match on feature name
   - Try fuzzy match (partial names, similar words)

2. If match found in Notion, extract:
   - `Feature name` (title field)
   - `Team` (relation to Teams DB)
   - `Sizing (team)` (e.g., "4-6 weeks")
   - `Sizing confidence` (Low/Medium/High)
   - `Timeline` (start and end dates)
   - `Priority` (Done, Now, Next, Later, Idea)
   - `Tech lead` (rollup from Team)
   - `Product manager` (rollup from Team)
   - `Engineering Manager` (rollup from Team)
   - `Status` (Notion status field)

3. If no match found, mark as `null` in the enrichment section

---

## Step 4: Save to JSON Database

**File location:** `~/_apps/_claude/cto-reports/project-data/project-updates.json`

**Structure:**
```json
{
  "last_updated": "[ISO 8601 timestamp]",
  "date_range_days": 7,
  "projects": {
    "[channel-name]": {
      "channel_name": "[name]",
      "channel_id": "[id]",
      "updates": [
        {
          "date": "YYYY-MM-DD",
          "timestamp": "[ISO 8601]",
          "feature": "[feature name]",
          "status": "[status]",
          "health": "[health status]",
          "health_indicator": "[emoji]",
          "release_date": "[date]",
          "completion_percentage": 75,
          "summary_text": "[full update text]",
          "slack_message_link": "[link]",
          "author": "[name]",
          "extracted_at": "[ISO 8601]"
        }
      ],
      "notion_enrichment": {
        "feature_name": "[name or null]",
        "team": "[team name or null]",
        "sizing": "[sizing or null]",
        "sizing_confidence": "[confidence or null]",
        "timeline_start": "[date or null]",
        "timeline_end": "[date or null]",
        "priority": "[priority or null]",
        "tech_lead": "[name or null]",
        "product_manager": "[name or null]",
        "engineering_manager": "[name or null]",
        "notion_status": "[status or null]",
        "last_synced": "[ISO 8601]"
      }
    }
  }
}
```

**Important:**
- If the JSON file exists, MERGE new data with existing (don't overwrite)
- Keep historical updates in the `updates` array
- Update `notion_enrichment` with latest data
- If a project has no updates in this scan, leave it unchanged in the file

---

## Step 5: Generate Summary Report

Create a human-readable summary:

```markdown
# Project Updates Report
Generated: [Current Date and Time]
Date Range: Last [X] days

## Summary
- **Projects with updates:** [count]
- **🔴 Critical health:** [count]
- **🟡 Warning health:** [count]
- **🟢 Healthy:** [count]
- **No updates found:** [count]

---

## 🔴 Critical Projects

### [Project Name]
**Channel:** #[channel-name]
**Latest Update:** [date]
- **Feature:** [name]
- **Status:** [status]
- **Health:** [health] 🔴
- **Release Date:** [date] ([percentage]%)
- **Team:** [team from Notion]
- **Tech Lead:** [name from Notion]

**Summary:** [brief summary of update]

---

## 🟡 Warning Projects

[Same format as Critical]

---

## 🟢 Healthy Projects

[Same format, shorter details]

---

## Projects With No Updates

These channels had no updates in the past [X] days:
- #[channel-name-1]
- #[channel-name-2]

---

## Data Storage

✅ All updates saved to: `cto-reports/project-data/project-updates.json`

Use this data for:
- Trend analysis over time
- Weekly reviews with `/weekly-review`
- Deep dives with `/check-project-deep <name>`
```

**Save this report to:** `~/_apps/_claude/cto-reports/project-updates-[YYYY-MM-DD].md`

---

## Important Notes

- **Parse variations:** The update format may vary slightly - be flexible in parsing
- **Emoji handling:** Extract health indicators from emojis (🟢 = healthy, 🟡 = warning, 🔴 = critical)
- **Missing fields:** If a field is missing in the update (e.g., no completion %), set to null
- **Error handling:** If Slack or Notion fails, note it in the report but continue processing other projects
- **Performance:** Aim to complete in 2-5 minutes depending on number of channels
- **Partial matches:** For Notion enrichment, try your best to match but don't stress if no match found
