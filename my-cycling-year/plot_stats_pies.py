import sys
import os
import json
import datetime
from pylab import *

# pass activity directory as command-line argument!
# year of concern as second argument
# and list of activity types to explicitly include in pie chart as third argument

types = []
type_count = {}
type_time = {}
with open(sys.argv[3]) as typefile:
    for line in typefile:
        type = line.strip().strip('\n')
        types.append(type)
        type_count[type] = 0
        type_time[type] = 0.
    types.append('Other')
    type_count['Other'] = 0
    type_time['Other'] = 0.

gears = []
gear_count = {}
gear_dist = {}
gear_time = {}

for root, dirs, files in os.walk(str(sys.argv[1]), topdown=True):
    for act_filename in files:
        with open(os.path.join(root, act_filename)) as act_file:
            act_json = json.load(act_file)
            print(act_json['type'])
            if act_json['start_date'].split('T')[0].split('-')[0] != sys.argv[2]:
                continue
            try:
                gear_name = act_json['gear']['name']
            except:
                gear_name = None

            if gear_name:
                if not gear_name in gears:
                    gears.append(gear_name)
                    gear_count[gear_name] = 0
                    gear_dist[gear_name] = 0.
                    gear_time[gear_name] = 0.
                gear_count[gear_name] += 1
                gear_dist[gear_name] += act_json['distance']/1000.
                gear_time[gear_name] += act_json['moving_time']/3600.

            type = act_json['type']
            if act_json['commute']:
                type = 'Commute' # overwrite type
            if not type in types:
                type = 'Other'
            type_count[type] += 1
            type_time[type] += act_json['moving_time']/3600.


print(gear_count)
print(gear_dist)
print(gear_time)

print(type_count)
print(type_time)

gear_total_time = 0.
for time in gear_time.values():
    gear_total_time += time

gear_total_dist = 0.
for dist in gear_dist.values():
    gear_total_dist += dist

type_total_time = 0.
for time in type_time.values():
    type_total_time += time

figure()
pie(gear_time.values(), labels=gear_time.keys(), autopct='%1.1f%%', shadow=False, startangle=0)
axis('equal')
title('Shares of riding time (' + str(int(gear_total_time)) + 'h)')

figure()
pie(gear_dist.values(), labels=gear_dist.keys(), autopct='%1.1f%%', shadow=False, startangle=0)
axis('equal')
title('Shares of riding distance (' + str(int(gear_total_dist)) + 'km)')

figure()
pie(type_time.values(), labels=type_time.keys(), autopct='%1.1f%%', shadow=False, startangle=0)
axis('equal')
title('Shares of activity time (' + str(int(type_total_time)) + 'h)')

#tight_layout()
show()
