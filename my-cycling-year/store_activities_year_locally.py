from stravaio import StravaIO
import get_token

client = StravaIO(access_token=get_token.token['access_token'])

# Store Athlete
athlete = client.get_logged_in_athlete()
athlete.store_locally()

# Generate list of local athletes
local_athl_gen = client.local_athletes()
local_athl_ids = []
for athl in local_athl_gen:
    local_athl_ids.append(athl['id'])

# Generate list of local activities
local_act_ids = []
for athl_id in local_athl_ids:
    local_acts_gen = client.local_activities(athl_id)
    for act in local_acts_gen:
        local_act_ids.append(act['id'])

# Store Activities
list_activities = client.get_logged_in_athlete_activities(after='last year')
for a in list_activities:
    if a.id not in local_act_ids:
        client.get_activity_by_id(a.id).store_locally()
