import requests
import time
import argparse
import sys
from datetime import datetime

# --- CONFIGURATION ---
BASE_URL = "https://www.strava.com/api/v3"

def get_headers(access_token):
    return {'Authorization': f"Bearer {access_token}"}

def get_epoch_timestamps(year):
    """Returns start and end epoch timestamps for the given year."""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)
    return int(start_date.timestamp()), int(end_date.timestamp())

def get_gear_ids(access_token):
    """
    Fetches the authenticated athlete's profile to map bike names to IDs.
    Returns a dictionary: {'Bike Name': 'b12345'}
    """
    url = f"{BASE_URL}/athlete"
    response = requests.get(url, headers=get_headers(access_token))

    if response.status_code != 200:
        print(f"Error fetching profile: {response.text}")
        return None

    athlete = response.json()
    bikes = athlete.get('bikes', [])

    # Create a map of Bike Name -> Bike ID
    gear_map = {bike['name']: bike['id'] for bike in bikes}

    return gear_map

def get_activities(year, access_token):
    """
    Fetches all activities for the given year using pagination.
    """
    start_epoch, end_epoch = get_epoch_timestamps(year)
    activities = []
    page = 1
    per_page = 50

    print(f"Fetching activities for {year}...")

    while True:
        url = f"{BASE_URL}/athlete/activities"
        params = {
            'after': start_epoch,
            'before': end_epoch,
            'page': page,
            'per_page': per_page
        }

        response = requests.get(url, headers=get_headers(access_token), params=params)

        if response.status_code != 200:
            print(f"Error fetching activities: {response.text}")
            break

        data = response.json()

        if not data:
            break

        activities.extend(data)
        print(f"Fetched page {page} ({len(data)} activities)")
        page += 1

    return activities

def main():
    # --- ARGUMENT PARSING ---
    parser = argparse.ArgumentParser(description="Update Strava activities based on visibility and gear.")

    parser.add_argument("--token", required=True, help="Your Strava API Access Token")
    parser.add_argument("--year", type=int, required=True, help="The year to filter activities (e.g., 2023)")
    parser.add_argument("--old-bike", required=True, help="The exact name of the bike currently assigned (e.g., 'Giant Propel')")
    parser.add_argument("--new-bike", required=True, help="The exact name of the bike to change to (e.g., 'Canyon Grail AW')")
    parser.add_argument("--dry-run", action="store_true", help="If set, script will only simulate changes without updating data.")

    args = parser.parse_args()

    # --- SCRIPT LOGIC ---
    print("--- Step 1: Resolving Gear IDs ---")
    gear_map = get_gear_ids(args.token)
    if not gear_map:
        print(f"Error: Athlete returned without 'bikes'. Please make sure the token has 'profile:read_all' scope.")
        return

    old_gear_id = gear_map.get(args.old_bike)
    new_gear_id = gear_map.get(args.new_bike)

    if not old_gear_id:
        print(f"Error: Could not find bike named '{args.old_bike}' in your profile.")
        print(f"Available bikes found: {list(gear_map.keys())}")
        return

    if not new_gear_id:
        print(f"Error: Could not find bike named '{args.new_bike}' in your profile.")
        print(f"Available bikes found: {list(gear_map.keys())}")
        return

    print(f"IDs Resolved\n  Old: {old_gear_id} ({args.old_bike})\n  New: {new_gear_id} ({args.new_bike})")

    # 2. Fetch all activities for the year
    print(f"\n--- Step 2: Fetching History for {args.year} ---")
    all_activities = get_activities(args.year, args.token)

    # 3. Filter activities
    target_activities = [
        act for act in all_activities
        if act.get('private') is True and act.get('gear_id') == old_gear_id
    ]

    print(f"\n--- Step 3: Analysis ---")
    print(f"Total entries found for {args.year}: {len(all_activities)}")
    print(f"Entries matching criteria (Private + {args.old_bike}): {len(target_activities)}")

    if len(target_activities) == 0:
        print("No matching activities found to update.")
        return

    # 4. Update activities
    print(f"\n--- Step 4: {('DRY RUN ' if args.dry_run else '')}Update Process ---")

    for activity in target_activities:
        act_id = activity['id']
        act_name = activity.get('name', 'Unknown')
        act_date = activity.get('start_date_local', 'Unknown Date')

        if args.dry_run:
            print(f"[DRY RUN] Would update ID {act_id} | Date: {act_date} | Name: '{act_name}'")
            print(f"           -> Set Gear to '{args.new_bike}'")
            print(f"           -> Set Commute to True")
        else:
            print(f"Updating activity {act_id}: '{act_name}'...")
            update_url = f"{BASE_URL}/activities/{act_id}"
            payload = {
                'gear_id': new_gear_id,
                'commute': True
            }

            update_response = requests.put(update_url, headers=get_headers(args.token), data=payload)

            if update_response.status_code == 200:
                print("  -> Success")
            else:
                print(f"  -> Failed: {update_response.text}")

            # Rate limit protection
            time.sleep(0.5)

if __name__ == "__main__":
    main()
