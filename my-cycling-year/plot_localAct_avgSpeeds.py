import sys
import os
import json
import datetime
from pylab import *
from scipy.stats import kde
from matplotlib import dates

# pass activity directory as command-line argument!
# pass the year of concern as second command-line argument

data_dict_all = {}
data_dict_pm = {}

for root, dirs, files in os.walk(str(sys.argv[1]), topdown=True):
    for act_filename in files:
        with open(os.path.join(root, act_filename)) as act_file:
            act_json = json.load(act_file)
            if act_json['start_date'].split('T')[0].split('-')[0] != sys.argv[2]:
                continue
            print(act_json['start_date'])
            try:
                gear_name = act_json['gear']['name']
            except:
                gear_name = None
            if gear_name and not act_json['commute']:
                if not gear_name in data_dict_all.keys():
                    data_dict_all[gear_name] = [[], [], [], []] # date, speed, watts, kcal
                data_dict_all[gear_name][0].append(datetime.datetime.strptime(act_json['start_date'].split('T')[0], '%Y-%m-%d'))
                data_dict_all[gear_name][1].append(3.6*act_json['average_speed'])
                data_dict_all[gear_name][2].append(act_json['average_watts'])
                data_dict_all[gear_name][3].append(act_json['calories'])
                if act_json['device_watts']:
                    if not gear_name in data_dict_pm.keys():
                        data_dict_pm[gear_name] = [[], [], [], []] # date, avg pow, NP, max pow
                    data_dict_pm[gear_name][0].append(datetime.datetime.strptime(act_json['start_date'].split('T')[0], '%Y-%m-%d'))
                    data_dict_pm[gear_name][1].append(act_json['average_watts'])
                    data_dict_pm[gear_name][2].append(act_json['weighted_average_watts'])
                    data_dict_pm[gear_name][3].append(act_json['max_watts'])

figure()
for gear_name in data_dict_all:
    plot(data_dict_all[gear_name][0], data_dict_all[gear_name][1], 'o')
legend(data_dict_all.keys())

figure()
for gear_name in data_dict_all:
    plot(data_dict_all[gear_name][0], data_dict_all[gear_name][2], 'o')
legend(data_dict_all.keys())

figure()
for gear_name in data_dict_pm:
    plot(data_dict_pm[gear_name][0], data_dict_pm[gear_name][1], 'o')
legend(data_dict_pm.keys())

figure()
for gear_name in data_dict_pm:
    plot(data_dict_pm[gear_name][0], data_dict_pm[gear_name][2], 'o')
legend(data_dict_pm.keys())

figure()
for gear_name in data_dict_pm:
    plot(data_dict_pm[gear_name][0], data_dict_pm[gear_name][3], 'o')
legend(data_dict_pm.keys())


figure()
suptitle('Speeds and Watts over the year, by bicycle')

subplot(311)
for gear_name in data_dict_all:
    dates_num = dates.date2num(data_dict_all[gear_name][0])
    plot(dates_num, data_dict_all[gear_name][1], '*')
xlim(datetime.date(int(sys.argv[2])-1, 12, 25), datetime.date(int(sys.argv[2])+1, 1, 5))
#ylim(0)
xticks([])
ylabel('Avg. Speed [km/h]')

subplot(312)
for gear_name in data_dict_all:
    if gear_name in data_dict_pm:
        dates_num = dates.date2num(data_dict_pm[gear_name][0])
        plot(dates_num, data_dict_pm[gear_name][2], '*')
    else:
        dates_num = dates.date2num(data_dict_all[gear_name][0])
        null_data = []
        for date in dates_num:
            null_data.append(None)
        plot(dates_num, null_data, '*')
xlim(datetime.date(int(sys.argv[2])-1, 12, 25), datetime.date(int(sys.argv[2])+1, 1, 5))
#ylim(0)
xticks([])
ylabel('Weighted Power [W]')
legend(data_dict_all.keys())

subplot(313)
for gear_name in data_dict_all:
    if gear_name in data_dict_pm:
        dates_num = dates.date2num(data_dict_pm[gear_name][0])
        plot(dates_num, data_dict_pm[gear_name][3], '*')
    else:
        dates_num = dates.date2num(data_dict_all[gear_name][0])
        null_data = []
        for date in dates_num:
            null_data.append(None)
        plot(dates_num, null_data, '*')
xlim(datetime.date(int(sys.argv[2])-1, 12, 25), datetime.date(int(sys.argv[2])+1, 1, 5))
#ylim(0)
xlabel('Date')
ylabel('Max. Power [W]')

#setup dates formatting
ax = gca()
hfmt = dates.DateFormatter('%d.%m')
ax.xaxis.set_major_formatter(hfmt)

show()
