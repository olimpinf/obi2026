#!/usr/bin/env python3

import os.path

from reportlab.graphics import shapes
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.pdfbase.ttfonts import TTFont

import labels

# create Letter sheet
specs = labels.Specification(215.9, 279.4, 3, 10, 66.7, 25.4, 
                             corner_radius=2,
                             left_margin=5, right_margin=5,
                             top_margin=12.7, bottom_margin=12.7,
                             column_gap=3, row_gap=0)


# Get the path to the directory.
base_path = os.path.dirname(__file__)

# Create a function to draw each label. This will be given the ReportLab drawing
# object to draw on, the dimensions (NB. these will be in points, the unit
# ReportLab uses) of the label, and the name to put on the tag.
def write_address(label, width, height, address):
    label.add(shapes.String(20, height-12, 'Remetente:',
                            fontName="Helvetica-Bold", fontSize=8))
    i = 0
    for line in address:
        label.add(shapes.String(20, height-23-i*10, line,
                                fontName="Helvetica", fontSize=9))
        i += 1

# Create the sheet.
mysheet = labels.Sheet(specs, write_address, border=False)

address = [
    'Olimpíada Brasileira de Informática',
    'Instituto de Computação - UNICAMP',
    'Av. Albert Einstein, 1251',
    'Cidade Universitária Zeferino Vaz',
    '13083-852 Campinas SP'
]

mysheet.add_label(address,count=30)

# Save the file and we are done.
mysheet.save('etiquetas_remetente.pdf')
print("{0:d} label(s) output on {1:d} page(s).".format(mysheet.label_count, mysheet.page_count))
