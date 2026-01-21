#!/usr/bin/env python3

import sys

with open(sys.argv[1], "r") as f:
    lines = f.readlines()

old_emails = set()
for line in lines:
    level,id,email,name = line.split(',')
    old_emails.add(email)

with open(sys.argv[2], "r") as f:
    lines = f.readlines()

emails = {}
for line in lines:
    level,id,email,name = line.split(',')
    if email in old_emails:
        continue
    if email in emails.keys():
        emails[email].append(line)
    else:
        emails[email] = [line]


with open("emails_compet_unique_new.csv", "w") as f:
    for email in emails.keys():
        if len(emails[email]) == 1:
            f.write(emails[email][0])
