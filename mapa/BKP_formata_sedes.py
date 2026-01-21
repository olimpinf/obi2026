#!/usr/bin/env python
import sys

fin=open(sys.argv[1])
fin2=open(sys.argv[2])

cities_coord={}
for line in fin2.readlines(): #[2:]:
    line=line.split('|')
    #if len(line)!=4: continue
    city="%s-%s" % (line[0].strip(),line[1].strip())
    cities_coord[city]=[line[2].strip(),line[3].strip()]

cities={}
for line in fin.readlines(): #[2:]:

    try:
        line=line.split('|')
        #if len(line)<2: continue
        city="%s-%s" % (line[0].strip(),line[1].strip())
        if city not in cities.keys():
            cities[city]={"coords":cities_coord[city]}
        cities[city][line[2].strip()]=line[3].strip()
    except:
        print("problem with city", city, file=sys.stderr)
        print(line, file=sys.stderr)

for c in cities.keys():
    data=[c,cities[c]["coords"][0],cities[c]["coords"][1]]
    for level in ["school_address1"]:
        if level in cities[c].keys():
            data.append("%s=%s" % (level,cities[c][level]))
    print(",".join(data))
