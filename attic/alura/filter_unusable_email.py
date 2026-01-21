#!/usr/bin/env python3

import re
import sys
from unidecode import unidecode

def check_same_name(name1, name2):
    name1 = unidecode(name1).lower()
    name2 = unidecode(name2).lower()
    pattern = re.compile('[a-zA-Z ]+')
    re.sub(pattern, name1, name1)
    re.sub(pattern, name2, name2)
    if name1.find(name2) >= 0 or name2.find(name1) >= 0:
        return True    

    
    tokens1 = name1.split()
    tokens2 = name2.split()

    if len(tokens1) < len(tokens2):
        tokens1,tokens2 = tokens2,tokens1

    if len(tokens1) < 3:
        return False
    
    i,j = 0,0
    same = 0
    while i < len(tokens1) and j < len(tokens2):
        if tokens1[i] == tokens2[j]:
            same += 1
            i += 1
            j += 1
        elif i < len(tokens1):
            i += 1
        else:
            j += 1
    if len(tokens1) - same <= 1:
        return True
    return False

with open(sys.argv[1], "r") as f:
    lines = f.readlines()

emails = {}
for line in lines:
    level,id,email,name = line.split(',')
    if email.find('prof.educ') >= 0 or email.find('professor.educ') >= 0:
        continue
    #if level in ('PJ','P1','P2') and (email.find("aridesa") > 0 or email.find("objetivojuazeiro") > 0):
    #    continue
    if name.find('Test')>= 0 and name.find('Rafael') < 0 and name.find('Thuane') < 0 and name.find('Testoni') < 0 and name.find('Johann') < 0 and name.find('Claudia') < 0:
        continue
    if email in emails.keys():
        emails[email].append(line)
    else:
        emails[email] = [line]

with open("emails_compet_unique.csv", "w") as f:
    for email in emails.keys():
        if len(emails[email]) == 1:
            f.write(emails[email][0])

with open("emails_compet_not_unique_usable.csv", "w") as f:
    for email in emails.keys():
        if len(emails[email]) != 1 and len(emails[email]) <= 3:
            # check same person
            names = []
            for line in emails[email]:
                level,id,email,name = line.split(',')
                names.append(name)
            same = False
            for i in range(len(names)):
                for j in range(i+1,len(names)):
                    if check_same_name(names[i],names[j]):
                        same = True
            if same:
                f.write(emails[email][0])
            else:
                for line in emails[email]:
                    f.write(line)

with open("emails_compet_not_unique_not_usable.csv", "w") as f:
    for email in emails.keys():
        if len(emails[email]) > 3:
            for line in emails[email]:
                f.write(line)
