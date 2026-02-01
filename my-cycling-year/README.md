# my-cycling-year

The scripts are based on StravaIO v0.0.9, with the following modifications:

1) If there are virtual rides uploaded to Strava, the script for storing all
   activities will throw an error. To avoid it, a small change to the swagger_client
   package that comes with StravaIO is necessary. Line number 192 of the file
   `models/summary_segment.py` needs to be changed from

       `allowed_values = ["Ride", "Run"]  # noqa: E501`

   to

       `allowed_values = ["Ride", "Run", "VirtualRide"]  # noqa: E501`


2) If private activities should be included in the summary,
   line number 359 of stravaio.py needs to be changed from

       `"scope": "read,profile:read_all,activity:read",`

   to

       `"scope": "read_all,profile:read_all,activity:read_all",`


Also, it is normal that the script `store_activities_year_locally.py` does not
terminate by itself. It is unclear why and how to fix it, but after waiting
for a while it can be killed safely. Stored files can be found in `~/.stravadata`.
