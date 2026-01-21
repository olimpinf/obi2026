#!/usr/bin/env python3

import sys

with open(sys.argv[1], "r") as f:
    lines = f.readlines()

emails = {}
for line in lines:
    level,id,email,name = line.split(',')
    if email in emails.keys():
        emails[email].append(line)
    else:
        emails[email] = [line]

with open("emails_compet_unique.csv", "w") as f:
    for email in emails.keys():
        if len(emails[email]) == 1:
            f.write(emails[email][0])

with open("emails_compet_not_unique.csv", "w") as f:
    for email in emails.keys():
        if len(emails[email]) != 1:
            for line in emails[email]:
                f.write(line)
