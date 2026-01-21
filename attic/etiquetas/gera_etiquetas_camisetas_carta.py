#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import psycopg2
from psycopg2.extras import DictCursor
from reportlab.graphics import shapes

YEAR = 2021
import labels

# Consulta BD
conn = psycopg2.connect("host=localhost dbname=obi{} user=obi password=guga.LC".format(YEAR))
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)

def usage():
    print(sys.argv[0])

def clean(s):
    s = s.replace('\r',' ')
    return s

comm = '''select DISTINCT
    s.school_id,
    school_deleg_name,
    school_name,
    school_address,
    school_address_number,
    school_address_complement,
    school_address_district,
    school_zip,
    school_city,
    school_state 
from school as s, week as w, compet as c
where c.compet_id=w.compet_id and c.compet_school_id=s.school_id and tax_paid
order by s.school_id'''

curs.execute(comm)
bdata = curs.fetchall()
print('schools found:', len(bdata),file=sys.stderr)
schools = []

for data in bdata:
    deleg_name=data['school_deleg_name'].strip()
    names=deleg_name.split(' ')
    first=names[0].lower()
    if first.find('prof')==0:
        names=names[1:]
    deleg_name=" ".join(["Prof(a)."]+names)
    schools.append([deleg_name, clean(data['school_name']),data])

# now order by deleg_name, school_name
#schools.sort()


# create Letter sheet
specs = labels.Specification(sheet_width=215.9, sheet_height=279.4, columns=2, rows=5, 
                             label_width=101.6, label_height=50.8, 
                             corner_radius=4,
                             left_margin=4, right_margin=4,
                             top_margin=12.7, bottom_margin=12.7,
                             column_gap=4.8, row_gap=0)


# Get the path to the directory.
base_path = os.path.dirname(__file__)

# Create a function to draw each label. This will be given the ReportLab drawing
# object to draw on, the dimensions (NB. these will be in points, the unit
# ReportLab uses) of the label, and the name to put on the tag.
def write_address(label, width, height, address):
    i = 0
    tmp = split_line(address[0])
    for line in tmp:
        label.add(shapes.String(15, height-25-i*15, line,
                                fontName="Helvetica-Bold", fontSize=11))
        i += 1

    for line in address[2:]:
        tmp = split_line(line)
        for line_tmp in tmp:
            label.add(shapes.String(15, height-35-i*15, line_tmp,
                                    fontName="Helvetica", fontSize=11))
            i += 1
    label.add(shapes.String(250, height-35-i*15, address[1],
                                    fontName="Helvetica", fontSize=9))

# Create the sheet.
mysheet = labels.Sheet(specs, write_address, border=True)

def split_line(str,pos1=50,pos2=40):
    if str.isupper():
        pos1,pos2 = 40,30
    tmp = []
    if len(str) > pos1:
        space = str.find(' ',pos2)
        if space > 0:
            tmp.append(str[:space])
            tmp.append('       '+str[space+1:])
        else:
            tmp.append(str)
    else:
        tmp.append(str)
    return tmp

for s in schools:
    address = []
    address.append(clean(s[0]))    # deleg name is first item
    # school_number is second item
    address.append('e{:04}'.format(s[2]['school_id'])) 
    address.append(clean(s[1]))    # school name
    tmp = clean(s[2]['school_address'])
    if s[2]['school_address_number']:  
        tmp += ', ' + clean(s[2]['school_address_number'])
    address.append(tmp)
    if s[2]['school_address_complement']:  
        address.append(clean(s[2]['school_address_complement']))
    if s[2]['school_address_district']:  
        address.append('Bairro ' + clean(s[2]['school_address_district']))
    tmp = ' '.join((s[2]['school_zip'], s[2]['school_city'], s[2]['school_state']))
    address.append(tmp)
    #address.append("") # white space
    mysheet.add_label(address)

# Save the file and we are done.
mysheet.save('etiquetas_camisetas.pdf')
print("{0:d} label(s) output on {1:d} page(s).".format(mysheet.label_count, mysheet.page_count))
