import urllib.request
import re
import sys
import os
import time
import statistics
from datetime import datetime
from operator import itemgetter
import heapq
import collections

total_requests = 0
total_malformed = 0
total_client_errors = 0
total_redirects = 0
month_logs = [[],[],[],[],[],[],[],[],[],[],[],[]]
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
daily_requests = []
weekly_requests = []
month_requests = []

file_names = []

def least_common_values(array, to_find=None):
    counter = collections.Counter(array)
    if to_find is None:
        return sorted(counter.items(), key=itemgetter(1), reverse=False)
    return heapq.nsmallest(to_find, counter.items(), key=itemgetter(1))


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def parse(log):
    print('PARSING NOW...')
    regex = '(.*?) - (.*) \[(.*?)\] (.*) (\d+) (.*)'

    global total_requests
    global total_malformed
    global total_client_errors
    global total_redirects
    global month_logs
    global daily_requests
    global weekly_requests
    global month_requests
    global file_names

    last_day = 0
    week_total = 0
    requests_day = 0

    lines = log.splitlines()

    #Main Parse For Loop
    for i in range(len(lines)):
        match = re.match(regex, lines[i])
        if match:
            curr_line = list(match.groups())

            #Date Processing
            date = datetime.strptime(curr_line[2].strip('[').split(':')[0], '%d/%b/%Y')
            month_logs[date.month - 1].append(lines[i])
            if date.weekday() == last_day:
                requests_day = requests_day + 1
                week_total = week_total + 1
            else:
                daily_requests.append(requests_day)
                requests_day = 1
                last_day = date.weekday()
                if date.weekday() == 0:
                    weekly_requests.append(week_total)
                    week_total = 0

            #Status Codes
            code = list(curr_line[4])
            if code[0] == '4':
                total_client_errors = total_client_errors + 1
            elif code[0] == '3':
                total_redirects = total_redirects + 1

            #Files
            request = curr_line[3].split(' ')
            file_names.append(request[1])
        else:
            total_malformed = total_malformed + 1

    total_requests = len(lines) - total_malformed

    monthwrite(month_names, month_logs)

def monthwrite(month_names, month_logs):
    global month_requests
    print('WRITING MONTH LOGS...')
    for i in range(len(month_logs)):
        file_name = month_names[i] + '.log'
        month_file = open(file_name, 'a')
        for d in range(len(month_logs[i])):
            month_file.write(month_logs[i][d] + '\n')
        month_file.close()
        month_requests.append(len(month_logs[i]))
def main():
    #Check if the log file is already saved
    if os.path.exists('output.log'):
        print('Found existing log file, using that.')
        f = open('output.log', 'r')
        log = f.read()
        parse(log)
    else:
        print('No log file found, downloading now.')
        url = 'https://s3.amazonaws.com/tcmg476/http_access_log'
        response = urllib.request.urlopen(url)
        log = response.read().decode()

        f = open('output.log', 'w+')
        f.write(log)
        f.close()

        parse(log)

if __name__ == '__main__':
    main()
    mc = collections.Counter(file_names).most_common()[0]
    lc = collections.Counter(file_names).most_common()[-1]
    cls()
    print('==========| Statistics |==========')
    print('Total Requests Made:: ' + str(total_requests))
    print('Total Malformed Requests:: ' + str(total_malformed) + ' - ' + str(round((total_malformed / total_requests)*100, 2)) + '%')
    print('Total Client Errors:: ' + str(total_client_errors) + ' - ' + str(round((total_client_errors / total_requests)*100, 2)) + '%')
    print('Total Redirects:: ' + str(total_redirects) + ' - ' + str(round((total_redirects / total_requests)*100, 2)) + '%')
    print('Average Requests Made Per Day:: ' + str(round(statistics.mean(daily_requests))))
    print('Average Requests Made Per Week:: ' + str(round(statistics.mean(weekly_requests))))
    print('Average Requests Made Per Month:: ' + str(round(statistics.mean(month_requests))))
    print('Most Common File:: ' + str(mc[0]))
    print('Least Common File:: ' + str(lc[0]))
