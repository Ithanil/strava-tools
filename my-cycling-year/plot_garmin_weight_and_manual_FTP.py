from pylab import *
from matplotlib import dates
import datetime

def month_str_to_number(month_str):
    months = {"Jan" : 1, "Feb" : 2, "Mrz" : 3, "Apr" : 4, "Mai" : 5, "Jun" : 6, "Jul" : 7, "Aug" : 8, "Sep" : 9, "Okt" : 10, "Nov" : 11, "Dez" : 12}
    return months[month_str]


# pass weight file as first argument, FTP file as second argument and as third argument the year
# currently works only for german Garmin output file

dates_weight = []
weights = []
trigger = False
with open(str(sys.argv[1])) as weight_file:
    for line in weight_file:
        if line[1] == " ":
            dates_weight.append(datetime.date(int(line.split()[3].split('"')[0]), month_str_to_number(line.split()[2]), int(line.split()[1])))
            trigger = True
        else:
            if trigger:
                weights.append(float(line.split(',')[1].split()[0]))
                trigger = False
            else:
                print("Note: Duplicate weight data line. The line was:")
                print(line)                
dates_weight = dates.date2num(dates_weight)
print(dates_weight)
print(weights)


dates_ftp = {}
ftps = {}
ftp_types = []
with open(str(sys.argv[2])) as ftp_file:
    for line in ftp_file:
        if line[0] != '#' and line[0] != '\n':
            lsplit = line[:-1].split(',')
            print(lsplit)
            ftp_type = str(lsplit[2]).strip().strip('"')
            if ftp_type not in ftp_types:
                ftp_types.append(ftp_type)
                dates_ftp[ftp_type] = []
                ftps[ftp_type] = []            
            dates_ftp[ftp_type].append(datetime.datetime.strptime(lsplit[0], '%Y-%m-%d'))
            ftps[ftp_type].append(float(lsplit[1]))
for ftp_type in ftp_types:
    dates_ftp[ftp_type] = dates.date2num(dates_ftp[ftp_type])
print(dates_ftp)
print(ftps)

figure()
suptitle('Evolution of weight and threshold power estimation\n over the course of year ' + sys.argv[3])
subplot(211)
plot(dates_weight, weights, 'o--')
xlim(datetime.date(int(sys.argv[3])-1, 12, 25), datetime.date(int(sys.argv[3])+1, 1, 5))
xticks([])
ylabel('Weight [kg]')

subplot(212)
for ftp_type in ftp_types:
    plot(dates_ftp[ftp_type], ftps[ftp_type], 'D')
xlabel('Date')
ylabel('Est. anaerobic threshold [W]')
xlim(datetime.date(int(sys.argv[3])-1, 12, 25), datetime.date(int(sys.argv[3])+1, 1, 5))
legend(ftp_types)

#setup dates formatting
ax = gca()
hfmt = dates.DateFormatter('%d.%m')
ax.xaxis.set_major_formatter(hfmt)

#tight_layout()
show()
