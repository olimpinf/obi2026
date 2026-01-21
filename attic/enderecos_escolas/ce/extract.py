#!/usr/bin/env python3

import csv
import pandas as pd
import os
import re
import sys
from io import StringIO

df = pd.read_csv(sys.argv[1],delimiter=',')

linenum = 0
for r in df.iterrows():
    linenum += 1
    if len(r[1])==0 or pd.isnull(r[1][0]):
        continue

    name = r[1][3]
    email = r[1][11]
    try:
        email = email.lower()
    except:
        continue

    if name.lower().find('ed esp') > 0:
        continue


    print(f"{name.strip()},{email.strip()},")
    
        
