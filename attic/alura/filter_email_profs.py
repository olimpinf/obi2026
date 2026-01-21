#!/usr/bin/env python3

import re
import sys
from unidecode import unidecode

# emails profs
emails_profs = set()
with open(sys.argv[1], "r") as f:
    lines = f.readlines()
for line in lines:
    try:
        email,name = line.split(',')
        emails_profs.add(email)
    except:
        print("error", line)
        
# emails compets
with open(sys.argv[2], "r") as f:
    lines = f.readlines()

emails = {}
count = 0
for line in lines:
    level,id,email,name = line.split(',')
    if email in emails_profs:
        count += 1
        continue
    if email in emails.keys():
        emails[email].append(line)
    else:
        emails[email] = [line]
print("professores",count)

with open("emails_compet_no_prof.csv", "w") as f:
    for email in emails.keys():
        for line in emails[email]:
            f.write(line)

