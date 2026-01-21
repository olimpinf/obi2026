#! /usr/bin/env python
# coding=utf-8

import sys

def build(filename):
  print('\n\nbuilding',filename,file=sys.stderr)
  sites=open(filename,"r").readlines()
  siteCoords=[]
  siteCity=[]
  siteInfo=[]
  line_num=0
  for line in sites:
    line_num+=1
    data=line.strip().split(",")
    if len(data)<3: continue # empty?
    PointsMap[data[0]]=(float(data[2]),float(data[1]))
    #try:

    #except:
    #  sys.stderr.write("** (warning) Invalid Input Line: %d\n" % line_num)
    siteCoords.append([data[2],data[1]])
    siteCity.append(data[0])
    info="<b>%s</b>" % data[0]
    for d in data[3:]:
      info+='<br>%s' % d
    siteInfo.append(info)
  return siteCoords,siteCity,siteInfo

if __name__=="__main__":

  Bounds=[7, -75, -35, -33]
  #Creating the PointsMap from the input data
  PointsMap={}

  siteCoords,siteCity,siteInfo=build(sys.argv[1])
  print("siteCoords=",siteCoords)
  print("siteCity=",siteCity)
  print("siteInfo=",siteInfo)

  siteCoords,siteCity,siteInfo=build(sys.argv[2])
  print("siteCoords2=",siteCoords)
  print("siteCity2=",siteCity)
  print("siteInfo2=",siteInfo)

  siteCoords,siteCity,siteInfo=build(sys.argv[3])
  print("siteCoords3=",siteCoords)
  print("siteCity3=",siteCity)
  print("siteInfo3=",siteInfo)

