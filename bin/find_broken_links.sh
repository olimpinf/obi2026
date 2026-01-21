#!/bin/bash

#wget --spider -r -nv -nd  -T 2 -l 6 -o broken_links.log http://143.106.73.36:8000
wget --spider -r -nv -nd  -T 2 -l 6 -o broken_links.log http://olimpiada.ic.unicamp.br

# to find broken links:
# grep -B1 "broken link" broken_links.log

# check the language, "broken link" may be "link quebrado"
