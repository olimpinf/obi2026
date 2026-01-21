#!/usr/bin/env python

import sys

with open(sys.argv[1], "r") as f:
    lines = f.readlines()

line_num = 0
csv = ""
i = 0
ok = False
for line in lines:
    line_num += 1
    if i == 0:
        if line.find("EE ")>=0:
            csv += '"' + line.strip() + '",'
            i = 1
            ok = True
            continue
        elif line.find("EE ")>=0 or line.find("CENTRO ")>=0:
            i = 1
            ok = False
            continue
    elif i == 1:
        if not ok:
            i = 2
            continue
        if line.find("@") > 0:
            csv += line.strip() + ","
            i = 2
            continue
    elif i == 2:
        if not ok:
            i = 0
            continue
        if  line.find("DIRETOR:") == 0:
            csv += '"' + line[len("DIRETOR:"):].strip() + '"\n'
            i = 0
            ok = False
            continue

    else:
        print("error", line_num)
        print("i",i)
        print(line)
        sys.exit()

print(csv)

