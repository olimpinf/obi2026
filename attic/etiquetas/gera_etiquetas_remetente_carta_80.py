#!/usr/bin/env python3

import os.path

from reportlab.graphics import shapes
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.pdfbase.ttfonts import TTFont

import labels

# create Letter sheet
specs = labels.Specification(sheet_width=215.9, sheet_height=279.4, columns=4, rows=20, 
                             label_width=44.45, label_height=12.7, 
                             corner_radius=2,
                             left_margin=14.5, right_margin=14.5,
                             top_margin=12.7, bottom_margin=12.7,
                             column_gap=3, row_gap=0)


# Get the path to the directory.
base_path = os.path.dirname(__file__)

# Create a function to draw each label. This will be given the ReportLab drawing
# object to draw on, the dimensions (NB. these will be in points, the unit
# ReportLab uses) of the label, and the name to put on the tag.
def write_address(label, width, height, address):
    label.add(shapes.String(6, height-8, 'Remetente:',
                            fontName="Helvetica-Bold", fontSize=7))
    i = 0
    for line in address:
        label.add(shapes.String(6, height-16-i*7, line,
                                fontName="Helvetica", fontSize=6))
        i += 1

# Create the sheet.
mysheet = labels.Sheet(specs, write_address, border=True)

address = [
    'OBI -- IC/Unicamp',
    'Av. Albert Einstein, 1251',
    '13083-852 Campinas SP'
]

mysheet.add_label(address,count=80)

# Save the file and we are done.
mysheet.save('etiquetas_remetente.pdf')
print("{0:d} label(s) output on {1:d} page(s).".format(mysheet.label_count, mysheet.page_count))
