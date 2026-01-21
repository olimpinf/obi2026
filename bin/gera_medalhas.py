#!/usr/bin/env python3

import sys,re,os


with open(sys.argv[1]) as f:
    data=f.read()

pat_obi=re.compile(".*(obi[0-9]+).*")
pat_level=re.compile(".*/(.*)\.html")

pat_comment=re.compile('<!--.*-->')
pat_center_begin=re.compile('<center>')
pat_center_end=re.compile('</center>')
pat_table_begin=re.compile('<table .*>')
pat_table_end=re.compile('</table>')
pat_title=re.compile('title:(.*)')
pat_template=re.compile('template:.*')
pat_paragraph=re.compile("<p>.*")
pat_end_paragraph=re.compile(".*</p>")
pat_img=re.compile('<img src="/static/img/medalhinha_(.*)\.gif.*')
pat_td=re.compile("<td.*>(.*)</td>\\n")
pat_tr_begin=re.compile("<tr.*>.*")
pat_tr_end=re.compile("</tr>")
pat_td_end=re.compile(".*</td>")
pat_sup=re.compile("<sup>.*</sup(>|\})")
pat_HM=re.compile("HM;.*")

obi=re.sub(pat_obi,"\\1",sys.argv[1]).upper()
level=re.sub(pat_level,"\\1",sys.argv[1])

data=re.sub(pat_comment,"",data)
data=re.sub(pat_template,"",data)
data=re.sub(pat_sup,"",data)
data=re.sub(pat_paragraph,"",data)
data=re.sub(pat_end_paragraph,"",data)
data=re.sub(pat_center_begin,"",data)
data=re.sub(pat_center_end,"",data)
data=re.sub(pat_table_begin,"",data)
data=re.sub(pat_table_end,"",data)
data=re.sub(pat_title,obi+";\\1",data)
data=re.sub(pat_img,"\\1</td>",data)
data=re.sub(pat_td,"\\1;",data)
data=re.sub(pat_td_end,"",data)
data=re.sub(pat_tr_begin,"",data)
data=re.sub(pat_tr_end,"",data)
data=data.strip()

# remove HM
data=re.sub(pat_HM,"",data)
# acerta colunas
data=re.sub("(Classif.;)","Medalha;\\1",data)
# remove extra lines
data=re.sub("(\\n)+","\\n",data)

with open('/tmp/{}_{}.csv'.format(obi,level), 'w') as f:
    f.write(data)
