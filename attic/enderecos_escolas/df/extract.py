#!/usr/bin/env python3

import sys
    
name = 'name'

filename = sys.argv[1]

with open(filename, "r") as f:
    lines = f.readlines()

count = 0
searching = ""
for i in range(len(lines)-1, 0, -1):
    line = lines[i]
    if line.find("@") > 0:
        line = line.replace("<br/>","")
        pos = line.find(";")
        if pos > 0:
            line = line[pos+1:]
        email = line.strip()
        searching = "ATIVA"
    else:
        if searching != "" and line.find(searching) >= 0:
            name = lines[i-1].replace("<br/>","")
            pos = name.find(";")
            if pos > 0:
                name = name[pos+1:]
            name = name.replace("&#160;", " ")
            name = name.strip()
            if name.find("EC ") != 0 and name.find("CEF ") != 0 and name.find("CED ") != 0 and name.find("CEM ") != 0 and name.find("CEP ") != 0:
                continue
            print(f"{name},{email}")
            searching = ""


