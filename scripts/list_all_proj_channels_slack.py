#!/usr/bin/env python3
"""
Slack Project Channel Auditor

This script lists all public and private channels starting with 'proj-',
checks their last activity, and verifies if a specific user is a member.

It automatically joins public channels to read their history, resolving
'not_in_channel' errors.

REQUIREMENTS:
- Python 3
- A '.env' file in the same directory containing your Slack Bot Token:
  SLACK_TOKEN=xoxb-your-token-here
"""

import urllib.request
import urllib.error
import urllib.parse
import json
import sys
import os
import time
from datetime import datetime

# --- CONFIGURATION ---
# The email of the user you want to check for membership in channels.
# The bot token MUST have the 'users:read.email' scope for this to work.
# Set FRESHA_EMAIL environment variable in ~/.zshrc
USER_EMAIL_TO_CHECK = os.environ.get("FRESHA_EMAIL", "")

# Channels older than this many days without a message are marked "dormant".
DORMANT_DAYS_THRESHOLD = 90

# Add a small delay between API calls to avoid rate limiting
API_CALL_DELAY = 1.0  # seconds
# --- END CONFIGURATION ---

def get_slack_token():
    """Reads the Slack token from a .env file or an environment variable."""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip().startswith('SLACK_TOKEN='):
                    return line.split('=', 1)[1].strip()
    
    token = os.environ.get('SLACK_TOKEN')
    if not token:
        print("Error: SLACK_TOKEN not found.", file=sys.stderr)
        print("Create a .env file with 'SLACK_TOKEN=xoxb-your-token' or set it as an environment variable.", file=sys.stderr)
        sys.exit(1)
    return token

def slack_api_call(endpoint, token, params=None, method='GET'):
    """A generic function to make calls to the Slack API with rate-limit handling."""
    base_url = "https://slack.com/api/"
    url = f"{base_url}{endpoint}"
    headers = {'Authorization': f'Bearer {token}'}
    
    data = None
    if method == 'POST':
        headers['Content-Type'] = 'application/json; charset=utf-8'
        data = json.dumps(params).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)
    else:  # GET
        if params:
            url += '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=headers)

    # Retry logic with rate-limit handling
    max_retries = 5
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode())
                if not response_data.get('ok'):
                    error = response_data.get('error', 'unknown_error')
                    # Don't retry on simple errors like 'not_in_channel'
                    print(f"  └─ API Error for '{endpoint}': {error}", file=sys.stderr)
                    return None
                
                # Add a small delay after successful calls to prevent rate limiting
                time.sleep(API_CALL_DELAY)
                return response_data  # Success! Exit the loop.

        except urllib.error.HTTPError as e:
            # Check if it's a rate-limiting error
            if e.code == 429:
                # The 'Retry-After' header tells us how many seconds to wait
                retry_after = int(e.headers.get('Retry-After', 60))
                print(f"  🚦 Rate limited on attempt {attempt + 1}/{max_retries}. Waiting for {retry_after} seconds before retrying...", file=sys.stderr)
                time.sleep(retry_after)
                # Continue to the next attempt in the loop
                continue
            else:
                # For other HTTP errors, fail immediately
                print(f"  └─ HTTP Error for '{endpoint}': {e.code} {e.reason}", file=sys.stderr)
                return None
        except urllib.error.URLError as e:
            print(f"  └─ URL Error for '{endpoint}': {e.reason}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"  └─ Exception for '{endpoint}': {e}", file=sys.stderr)
            return None
    
    # If we've exhausted all retries
    print(f"  └─ API call for '{endpoint}' failed after {max_retries} retries.", file=sys.stderr)
    return None

def get_all_channels(token):
    """Fetches all public and private channels using pagination."""
    print("Fetching all channels from Slack...")
    channels = []
    cursor = None
    page = 0
    
    while True:
        page += 1
        print(f"  Fetching page {page}...")
        params = {'limit': 1000,
                  'types': 'public_channel',
                  'exclude_archived': True}
        if cursor:
            params['cursor'] = cursor
        
        response = slack_api_call('conversations.list', token, params)
        if not response:
            print(f"  └─ Failed to fetch channels on page {page}.", file=sys.stderr)
            break
            
        new_channels = response.get('channels', [])
        channels.extend(new_channels)
        print(f"  └─ Got {len(new_channels)} channels on page {page} (total: {len(channels)})")
        
        cursor = response.get('response_metadata', {}).get('next_cursor')
        if not cursor:
            break
    
    print(f"Found {len(channels)} total channels.")
    return channels

def get_user_id(token, email):
    """Finds a user's ID by their email address."""
    print(f"Looking up user ID for {email}...")
    response = slack_api_call('users.lookupByEmail', token, {'email': email})
    if response and response.get('user'):
        user_id = response['user']['id']
        print(f"Found User ID: {user_id}")
        return user_id
    else:
        print(f"Warning: Could not find user with email '{email}'.", file=sys.stderr)
        print("  └─ Membership check for this user will be skipped.", file=sys.stderr)
        return None

def write_output_files(project_channels_data, output_dir='../tmp_output'):
    """Writes the project channels data to output directory in multiple formats."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Write JSON file
    json_file = os.path.join(output_dir, f'project_channels_{timestamp}.json')
    with open(json_file, 'w') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'total_channels': len(project_channels_data),
            'channels': project_channels_data
        }, f, indent=2)
    print(f"\n✅ JSON output written to: {json_file}")

    # Write markdown file
    md_file = os.path.join(output_dir, f'project_channels_{timestamp}.md')
    with open(md_file, 'w') as f:
        f.write(f"# Fresha Project Channels Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Channels:** {len(project_channels_data)}\n\n")
        f.write(f"---\n\n")

        for channel in project_channels_data:
            f.write(f"### {channel['name']}\n")
            f.write(f"- **Channel ID:** `{channel['channel_id']}`\n")
            f.write(f"- **Members:** {channel['members_count']}\n")
            f.write(f"- **Last Active:** {channel['last_active']}\n")
            f.write(f"- **Your Membership:** {'✅ Member' if channel['user_is_member'] == 'Yes' else '❌ Not a member'}\n")
            f.write(f"- **Dormant:** {channel['is_dormant']}\n")
            f.write(f"\n")

    print(f"✅ Markdown output written to: {md_file}")
    return json_file, md_file

def main():
    """Main execution function."""
    token = get_slack_token()
    user_id_to_check = get_user_id(token, USER_EMAIL_TO_CHECK)
    
    all_channels = get_all_channels(token)
    
    print("\nAuditing 'proj-' channels (this may take a moment)...")
    project_channels_data = []
    
    # Filter for project channels first
    proj_channels_to_audit = [
        c for c in all_channels
        if (c.get('name', '').startswith('proj-') or c.get('name', '').startswith('proj_'))
        and not c.get('is_archived', False)
    ]
    
    print(f"Found {len(proj_channels_to_audit)} 'proj-' channels to audit.\n")

    for i, channel in enumerate(proj_channels_to_audit):
        channel_id = channel['id']
        channel_name = channel['name']
        is_private = channel.get('is_private', False)
        is_member_of_channel = channel.get('is_member', False)
        
        print(f"Processing [{i+1}/{len(proj_channels_to_audit)}]: #{channel_name}")

        # If it's a public channel and we're not a member, join it.
        if not is_member_of_channel and not is_private:
            print(f"  ├─ Bot not a member. Joining public channel...")
            join_response = slack_api_call('conversations.join', token, {'channel': channel_id}, method='POST')
            if join_response:
                is_member_of_channel = True  # We are now a member
                print("  ├─ Join successful.")
            else:
                print("  └─ Failed to join. Cannot fetch details.")
        
        # Now, only proceed if we are a member (either initially or after joining)
        last_active_str = "Unknown"
        is_dormant_str = "Unknown"
        user_is_member_str = "N/A"

        if is_member_of_channel:
            # 1. Get last message time
            history = slack_api_call('conversations.history', token, {'channel': channel_id, 'limit': 1})
            if history and history.get('messages'):
                last_ts = float(history['messages'][0]['ts'])
                last_msg_time = datetime.fromtimestamp(last_ts)
                days_since = (datetime.now() - last_msg_time).days
                
                if days_since == 0:
                    last_active_str = "Today"
                elif days_since == 1:
                    last_active_str = "Yesterday"
                else:
                    last_active_str = f"{days_since} days ago"
                
                is_dormant_str = "Yes" if days_since >= DORMANT_DAYS_THRESHOLD else "No"
            else:
                last_active_str = "No messages"
                is_dormant_str = "Yes"

            # 2. Check for specific user membership
            if user_id_to_check:
                members_response = slack_api_call('conversations.members', token, {'channel': channel_id, 'limit': 200})
                # Note: This simple version doesn't handle pagination for channels > 200 members
                if members_response and members_response.get('members'):
                    user_is_member_str = "Yes" if user_id_to_check in members_response['members'] else "No"
                else:
                    user_is_member_str = "Error"
        elif is_private:
            last_active_str = "Private"
            is_dormant_str = "N/A"
            user_is_member_str = "N/A (Private)"

        project_channels_data.append({
            'name': channel_name,
            'channel_id': channel_id,
            'bot_is_member': "Yes" if is_member_of_channel else "No",
            'user_is_member': user_is_member_str,
            'members_count': channel.get('num_members', 0),
            'is_dormant': is_dormant_str,
            'last_active': last_active_str
        })
    
    # Sort and write output files
    project_channels_data.sort(key=lambda x: x['name'])

    print("\n--- Project Channel Audit Report ---")
    print(f"{'Channel Name':<30} | {'Channel ID':<15} | {'User Member':<12} | {'Dormant':<10} | {'Last Active':<15} | {'Users'}")
    print("-" * 120)
    for data in project_channels_data:
        print(f"{data['name']:<30} | {data['channel_id']:<15} | {data['user_is_member']:<12} | {data['is_dormant']:<10} | {data['last_active']:<15} | {data['members_count']}")

    # Write output files
    write_output_files(project_channels_data)

if __name__ == "__main__":
    main()
