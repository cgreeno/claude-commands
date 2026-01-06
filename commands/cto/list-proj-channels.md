---
description: List all project channels in Slack with membership status
---

Discover all project channels in Slack and show which ones the user is a member of.

**IMPORTANT: This command ALWAYS queries Slack directly and updates the projects file.**

**Steps:**

1. **Query Slack:** Run the Python script to get all project channels
   - Always print out when the script was last run to the user 
   - Execute: `python ~/.claude/scripts/list_all_proj_channels_slack.py`
   - This script paginates through ALL channels and filters for project channels matching:
     - `proj_*` (underscore prefix)
     - `proj-*` (hyphen prefix)
   - The script outputs JSON with channel details (ID, name, members, is_member, purpose, topic, is_dormant)
   - The script outputs into a directory "~/_apps/_claude/tmp_output/"
   - Parse the JSON output to get the channel list

2. **Read existing data:** Read `~/.claude/command_resources/projects_to_monitor.md` to see what projects are already tracked

3. **Update the file:** For EACH project channel found in Slack:
   - Check if the channel already exists in `~/.claude/command_resources/projects_to_monitor.md` (by channel ID or name)
   - If it does NOT exist, add a new entry with:
     - Channel name
     - Channel ID
     - Member count
     - User's membership status (is_member field)
     - Description/purpose (from purpose or topic fields)
     - Status (Active if not dormant, Dormant if is_dormant=true)
   - If it DOES exist, update the entry with current data:
     - Member count (may have changed)
     - User's membership status (may have changed)
     - Status (may have changed)
   - Update the "Last Updated" timestamp at the top of the file
   - Preserve the existing structure and any manual notes

4. **Sort channels:**
   - Separate into "Active" and "Dormant" sections
   - Sort alphabetically within each section

5. **Generate a report** in this format:

```markdown
# Project Channels Discovery Report
Generated: [Current Date and Time]

## ✅ Channels You're In ([count])

| Channel Name | Members | Purpose/Topic |
|--------------|---------|---------------|
| #proj_feature-name | 12 | [channel topic] |

## ❌ Channels You're NOT In ([count])

| Channel Name | Members | Purpose/Topic |
|--------------|---------|---------------|
| #proj_other-feature | 8 | [channel topic] |

---

## Next Steps

✅ All project channels have been saved to `~/.claude/command_resources/projects_to_monitor.md`

Review the file to:
- See detailed information for each project
- Add channels you want to actively monitor for `/check-projects`
- Join relevant channels using `/join #channel-name`
```

**Important:**
- ALWAYS query Slack fresh - never use cached data
- ALWAYS update projects_to_monitor.md with any new or changed channels
- Include member count to help assess activity level
- Include channel topic/purpose if available
- Mark channels as dormant if they have the is_dormant property
- Preserve user's manual edits to the monitoring list section
