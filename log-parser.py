import urllib.request
import re
import sys
import os
import time
import statistics
from datetime import datetime
from tqdm import tqdm

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def parse(log):
    regex = '(.*?) - (.*) \[(.*?)\] (.*) (\d+) (.*)'

    total_malformed = 0
    total_client_errors = 0
    total_redirects = 0

    month_logs = [[],[],[],[],[],[],[],[],[],[],[],[]]
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    daily_requests = []
    weekly_requests = []
    month_requests = []

    lines = log.splitlines()

    #Main Parse For Loop
    for i in tqdm(range(len(lines))):
        match = re.match(regex, lines[i])
        if match:
            curr_line = list(match.groups())

            #Date Processing
            date = datetime.strptime(curr_line[2].strip('[').split(':')[0], '%d/%b/%Y')
            month_logs[date.month - 1].append(lines[i])

            #Status Codes
            code = list(curr_line[4])
            if code[0] == '4':
                total_client_errors += 1
            elif code[0] == '3':
                total_redirects += 1
        else:
            total_malformed += 1

    total_requests = len(lines) - total_malformed
    print('Total Requests Made:: ' + str(total_requests))
    print('Total Malformed Requests:: ' + str(total_malformed))
    print('Total Client Errors:: ' + str(total_client_errors))
    print('Total Redirects:: ' + str(total_redirects))

def monthwrite():
    print('WRITING MONTH LOGS...')
    for i in range(len(month_logs)):
        file_name = month_names[i] + '.log'
        month_file = open(string_name, 'a')
        for d in range(len(month_logs[i])):
            month_file.write(month_logs[i][d] + '\n')
        month_file.close()
def main():
    #Check if the log file is already saved
    if os.path.exists('output.log'):
        f = open('output.log', 'r')
        log = f.read()
        parse(log)
    else:
        url = 'https://s3.amazonaws.com/tcmg476/http_access_log'
        response = urllib.request.urlopen(url)
        log = response.read().decode()

        f = open('output.log', 'w+')
        f.write(log)
        f.close()

        parse(log)

if __name__ == '__main__':
    main()
