import os
import sys


def medal_cuts(level,year,return_all=False):
  print("year is ",year)
  if year==2025:
    if level==1:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD =  14 # 18 # 8 # 18 #16 # 22 # 19 #25 #20 # 19 # 21 # 12 # 11
      CUT_SILVER = 64 # 35 # 27 # 46 # 44 # 59 # 66 #72 #58 # 57 # 64 # 49 # 37
      CUT_BRONZE = 139 #54 # 42 # 73 # 79 # 135  # 125  #132 #114 # 115 # 146 # 109 # 107
      CUT_HONORS = 139 #102 # 98 # 122 # 184 #210 #181 # 195 # 239 # 143
      mod,level,total='Iniciação','1', 18763 # 20573 # 26280 # 19686 # 11645 #22026 #23364
    elif level==2:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 50
      CUT_GOLD = 12 #20 #23 # 21 # 32 # 39 # 17 #24 #21 # 22 # 20 # 15 # 13
      CUT_SILVER = 44 # 62 #57 # 61 # 61 # 67 # 63 # 64  #62 #66 # 55 # 67 # 40 # 37
      CUT_BRONZE = 127 #137 # 111 # 102 # 103 # 117 # 138 # 124 #123 #134 # 127 # 122 # 101 # 104
      CUT_HONORS = 127 # 433 # 167 # 157 #141 # 149 # 192 # 212 #192 #212 # 216 # 251 # 137
      mod,level,total='Iniciação','2', 17349 # 19423 # 26819 # 11935 # 21152 #24134
    elif level==3:
      NUM_POINTS_PHASE_1= 300 #400 # 300
      NUM_POINTS_PHASE_2= 400 # 400
      NUM_POINTS_PHASE_3= 400
      CUT_GOLD = 6 # 6 # 5 # 7 # 6 # 3 # 6 # 5 #2 #2 # 1 # 2 # 5 # 24
      CUT_SILVER = 17 # 14 # 16 # 18 # 17 # 9 # 11 # 7 #4 #7 # 3 # 8 # 16 # 38
      CUT_BRONZE = 48 #31 # 29 # 31 # 28 # 20 # 20 #11 #24 # 8 # 20 # 35 # 50
      CUT_HONORS = 48 # 100 # 40 # 47 # 47 # 31 # 30 # 28 #27 #27 # 16 # 39 # 58
      mod,level,total='Programação','1', 3240 # 2261 # 7450 # 6028 # 3250 # 3295 #2600
    elif level==4:
      NUM_POINTS_PHASE_1=400 #500
      NUM_POINTS_PHASE_2=400# 500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD = 7 # 6 # 5 # 3 # 5 # 7 # 5 # 10 #4 #4 # 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 21 # 17 #12 # 11 # 18 # 12 # 15 # 14 # 12 #10 # 8 # 7 # 9 # 12 # 11
      CUT_BRONZE = 50 # 23 # 23 # 32 # 31 # 22 # 22 # 22 #15 # 17 # 16 # 18 # 17 # 15
      CUT_HONORS = 50 # 33 # 34 # 49 # 43 # 42 # 33 #24 # 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2', 6762 # 5609 # 14549 # 10462 # 5747 # 6471 # 5137
    elif level==5:
      NUM_POINTS_PHASE_1=300 #300
      NUM_POINTS_PHASE_2=400 #400
      NUM_POINTS_PHASE_3=400
      CUT_GOLD = 8 # 5 # 8 # 7 # 6 # 6 # 3 # 3 #1 #1 # 1 # 1 # 2 % 23
      CUT_SILVER = 23 #20 # 16 # 19 # 17 # 14 # 11  # 13 #7 #4 # 4 # 4 # 10 # 32
      CUT_BRONZE = 49 #28 # 23 # 41 # 27 # 34 # 27 # 29  #12 #9 # 9 # 15 # 17 # 35
      CUT_HONORS = 49 # 37 # 33 # 67 # 47 # 41 # 50 #46 #36 #18 # 15 # 25 # 22
      mod,level,total='Programação','Júnior', 609 # 724 # 2691 # 2471 # 1608 # 715  #982
    elif level==6:
      NUM_POINTS_PHASE_1=400 #500
      NUM_POINTS_PHASE_2=400 #500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD = 2 # 6 # 5 # 12 # 7 # 5 # 5 # 9 #4 #3 # 1 # 2
      CUT_SILVER = 15 # 18 #13 # 19 # 14 # 11 # 9 # 11 #8 #4 # 5 # 6
      CUT_BRONZE = 33 #30 # 34 # 29 # 22 # 18 # 20 #16 #11 # 14 # 12
      CUT_HONORS = 33 #51 # 51 # 34 # 29 # 34 # 34 #27 #28 # 26 # 24
      mod,level,total='Programação','Sênior', 1940 # 1487 # 1883 # 1512 # 1991 # 1821
    elif level==7:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 30
      CUT_GOLD = 9 # 17 #11 # 9 # 14 # 17 # 16 # 17
      CUT_SILVER = 64 # 54 #22 # 22 # 33 # 36 # 44 # 50
      CUT_BRONZE = 122 # 120 #51 # 49 # 62 # 59 # 85 # 98
      CUT_HONORS = 122 # 473 #85 # 84 # 100 # 92 # 167 # 220
      mod,level,total='Iniciação','Júnior', 16273 # 14479 #19991 # 16268 # 8352 #13674 # 15345    
  elif year==2024:
    if level==1:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD =  16 # 18 # 8 # 18 #16 # 22 # 19 #25 #20 # 19 # 21 # 12 # 11
      CUT_SILVER = 50 # 35 # 27 # 46 # 44 # 59 # 66 #72 #58 # 57 # 64 # 49 # 37
      CUT_BRONZE = 106 #54 # 42 # 73 # 79 # 135  # 125  #132 #114 # 115 # 146 # 109 # 107
      CUT_HONORS = 183 #102 # 98 # 122 # 184 #210 #181 # 195 # 239 # 143
      mod,level,total='Iniciação','1', 20573 # 26280 # 19686 # 11645 #22026 #23364
    elif level==2:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 50
      CUT_GOLD = 20 #23 # 21 # 32 # 39 # 17 #24 #21 # 22 # 20 # 15 # 13
      CUT_SILVER = 62 #57 # 61 # 61 # 67 # 63 # 64  #62 #66 # 55 # 67 # 40 # 37
      CUT_BRONZE = 137 # 111 # 102 # 103 # 117 # 138 # 124 #123 #134 # 127 # 122 # 101 # 104
      CUT_HONORS = 233 # 167 # 157 #141 # 149 # 192 # 212 #192 #212 # 216 # 251 # 137
      mod,level,total='Iniciação','2', 19423 # 26819 # 11935 # 21152 #24134
    elif level==3:
      NUM_POINTS_PHASE_1= 300 #400 # 300
      NUM_POINTS_PHASE_2= 400 # 400
      NUM_POINTS_PHASE_3= 400
      CUT_GOLD = 6 # 5 # 7 # 6 # 3 # 6 # 5 #2 #2 # 1 # 2 # 5 # 24
      CUT_SILVER = 14 # 16 # 18 # 17 # 9 # 11 # 7 #4 #7 # 3 # 8 # 16 # 38
      CUT_BRONZE = 31 # 29 # 31 # 28 # 20 # 20 #11 #24 # 8 # 20 # 35 # 50
      CUT_HONORS = 51 # 40 # 47 # 47 # 31 # 30 # 28 #27 #27 # 16 # 39 # 58
      mod,level,total='Programação','1', 2261 # 7450 # 6028 # 3250 # 3295 #2600
    elif level==4:
      NUM_POINTS_PHASE_1=400 #500
      NUM_POINTS_PHASE_2=400# 500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD = 6 # 5 # 3 # 5 # 7 # 5 # 10 #4 #4 # 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 17 #12 # 11 # 18 # 12 # 15 # 14 # 12 #10 # 8 # 7 # 9 # 12 # 11
      CUT_BRONZE = 33 # 23 # 23 # 32 # 31 # 22 # 22 # 22 #15 # 17 # 16 # 18 # 17 # 15
      CUT_HONORS = 46 # 33 # 34 # 49 # 43 # 42 # 33 #24 # 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2', 5609 # 14549 # 10462 # 5747 # 6471 # 5137
    elif level==5:
      NUM_POINTS_PHASE_1=300 #300
      NUM_POINTS_PHASE_2=400 #400
      NUM_POINTS_PHASE_3=400
      CUT_GOLD = 6 # 5 # 8 # 7 # 6 # 6 # 3 # 3 #1 #1 # 1 # 1 # 2 % 23
      CUT_SILVER = 20 #20 # 16 # 19 # 17 # 14 # 11  # 13 #7 #4 # 4 # 4 # 10 # 32
      CUT_BRONZE = 31 #28 # 23 # 41 # 27 # 34 # 27 # 29  #12 #9 # 9 # 15 # 17 # 35
      CUT_HONORS = 43 # 37 # 33 # 67 # 47 # 41 # 50 #46 #36 #18 # 15 # 25 # 22
      mod,level,total='Programação','Júnior', 724 # 2691 # 2471 # 1608 # 715  #982
    elif level==6:
      NUM_POINTS_PHASE_1=400 #500
      NUM_POINTS_PHASE_2=400 #500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD = 6 # 5 # 12 # 7 # 5 # 5 # 9 #4 #3 # 1 # 2
      CUT_SILVER = 18 #13 # 19 # 14 # 11 # 9 # 11 #8 #4 # 5 # 6
      CUT_BRONZE = 34 #30 # 34 # 29 # 22 # 18 # 20 #16 #11 # 14 # 12
      CUT_HONORS = 57 #51 # 51 # 34 # 29 # 34 # 34 #27 #28 # 26 # 24
      mod,level,total='Programação','Sênior', 1487 # 1883 # 1512 # 1991 # 1821
    elif level==7:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 30
      CUT_GOLD = 17 #11 # 9 # 14 # 17 # 16 # 17
      CUT_SILVER = 54 #22 # 22 # 33 # 36 # 44 # 50
      CUT_BRONZE = 120 #51 # 49 # 62 # 59 # 85 # 98
      CUT_HONORS = 173 #85 # 84 # 100 # 92 # 167 # 220
      mod,level,total='Iniciação','Júnior', 14479 #19991 # 16268 # 8352 #13674 # 15345    
  elif year==2023:
    if level==1:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD =  18 # 8 # 18 #16 # 22 # 19 #25 #20 # 19 # 21 # 12 # 11
      CUT_SILVER = 35 # 27 # 46 # 44 # 59 # 66 #72 #58 # 57 # 64 # 49 # 37
      CUT_BRONZE = 54 # 42 # 73 # 79 # 135  # 125  #132 #114 # 115 # 146 # 109 # 107
      CUT_HONORS = 102 # 98 # 122 # 184 #210 #181 # 195 # 239 # 143
      mod,level,total='Iniciação','1', 17415 # 19686 # 11645 #22026 #23364
    elif level==2:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 50
      CUT_GOLD = 23 # 21 # 32 # 39 # 17 #24 #21 # 22 # 20 # 15 # 13
      CUT_SILVER = 57 # 61 # 61 # 67 # 63 # 64  #62 #66 # 55 # 67 # 40 # 37
      CUT_BRONZE =  111 # 102 # 103 # 117 # 138 # 124 #123 #134 # 127 # 122 # 101 # 104
      CUT_HONORS =  167 # 157 #141 # 149 # 192 # 212 #192 #212 # 216 # 251 # 137
      mod,level,total='Iniciação','2', 17703 # 11935 # 21152 #24134
    elif level==3:
      NUM_POINTS_PHASE_1= 300 #400 # 300
      NUM_POINTS_PHASE_2= 400 # 400
      NUM_POINTS_PHASE_3= 400
      CUT_GOLD =  5 # 7 # 6 # 3 # 6 # 5 #2 #2 # 1 # 2 # 5 # 24
      CUT_SILVER =  16 # 18 # 17 # 9 # 11 # 7 #4 #7 # 3 # 8 # 16 # 38
      CUT_BRONZE =  29 # 31 # 28 # 20 # 20 #11 #24 # 8 # 20 # 35 # 50
      CUT_HONORS =  40 # 47 # 47 # 31 # 30 # 28 #27 #27 # 16 # 39 # 58
      mod,level,total='Programação','1', 2802 # 6028 # 3250 # 3295 #2600
    elif level==4:
      NUM_POINTS_PHASE_1=400 #500
      NUM_POINTS_PHASE_2=400# 500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  5 # 3 # 5 # 7 # 5 # 10 #4 #4 # 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 12 # 11 # 18 # 12 # 15 # 14 # 12 #10 # 8 # 7 # 9 # 12 # 11
      CUT_BRONZE =  23 # 23 # 32 # 31 # 22 # 22 # 22 #15 # 17 # 16 # 18 # 17 # 15
      CUT_HONORS =  33 # 34 # 49 # 43 # 42 # 33 #24 # 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2', 5263 # 10462 # 5747 # 6471 # 5137
    elif level==5:
      NUM_POINTS_PHASE_1=300 #300
      NUM_POINTS_PHASE_2=400 #400
      NUM_POINTS_PHASE_3=400
      CUT_GOLD =  5 # 8 # 7 # 6 # 6 # 3 # 3 #1 #1 # 1 # 1 # 2 % 23
      CUT_SILVER = 20 # 16 # 19 # 17 # 14 # 11  # 13 #7 #4 # 4 # 4 # 10 # 32
      CUT_BRONZE = 28 # 23 # 41 # 27 # 34 # 27 # 29  #12 #9 # 9 # 15 # 17 # 35
      CUT_HONORS =  37 # 33 # 67 # 47 # 41 # 50 #46 #36 #18 # 15 # 25 # 22
      mod,level,total='Programação','Júnior', 706 # 2471 # 1608 # 715  #982
    elif level==6:
      NUM_POINTS_PHASE_1=400 #500
      NUM_POINTS_PHASE_2=400 #500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  5 # 12 # 7 # 5 # 5 # 9 #4 #3 # 1 # 2
      CUT_SILVER = 13 # 19 # 14 # 11 # 9 # 11 #8 #4 # 5 # 6
      CUT_BRONZE = 30 # 34 # 29 # 22 # 18 # 20 #16 #11 # 14 # 12
      CUT_HONORS = 51 # 51 # 34 # 29 # 34 # 34 #27 #28 # 26 # 24
      mod,level,total='Programação','Sênior', 1708 # 1883 # 1512 # 1991 # 1821
    elif level==7:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 30
      CUT_GOLD = 11 # 9 # 14 # 17 # 16 # 17
      CUT_SILVER = 22 # 22 # 33 # 36 # 44 # 50
      CUT_BRONZE = 51 # 49 # 62 # 59 # 85 # 98
      CUT_HONORS = 85 # 84 # 100 # 92 # 167 # 220
      mod,level,total='Iniciação','Júnior', 14514 # 16268 # 8352 #13674 # 15345    
  elif year==2022:
    if level==1:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD =  8 # 18 #16 # 22 # 19 #25 #20 # 19 # 21 # 12 # 11
      CUT_SILVER = 27 # 46 # 44 # 59 # 66 #72 #58 # 57 # 64 # 49 # 37
      CUT_BRONZE = 42 # 73 # 79 # 135  # 125  #132 #114 # 115 # 146 # 109 # 107
      CUT_HONORS = 98 # 122 # 184 #210 #181 # 195 # 239 # 143
      mod,level,total='Iniciação','1', 13699 # 11645 #22026 #23364
    elif level==2:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD = 21 # 32 # 39 # 17 #24 #21 # 22 # 20 # 15 # 13
      CUT_SILVER = 61 # 61 # 67 # 63 # 64  #62 #66 # 55 # 67 # 40 # 37
      CUT_BRONZE =  102 # 103 # 117 # 138 # 124 #123 #134 # 127 # 122 # 101 # 104
      CUT_HONORS =  157 #141 # 149 # 192 # 212 #192 #212 # 216 # 251 # 137
      mod,level,total='Iniciação','2', 14284 # 11935 # 21152 #24134
    elif level==3:
      NUM_POINTS_PHASE_1= 300 #400 # 300
      NUM_POINTS_PHASE_2= 400 # 400
      NUM_POINTS_PHASE_3= 400
      CUT_GOLD = 7 # 6 # 3 # 6 # 5 #2 #2 # 1 # 2 # 5 # 24
      CUT_SILVER = 18 # 17 # 9 # 11 # 7 #4 #7 # 3 # 8 # 16 # 38
      CUT_BRONZE = 31 # 28 # 20 # 20 #11 #24 # 8 # 20 # 35 # 50
      CUT_HONORS =  47 # 47 # 31 # 30 # 28 #27 #27 # 16 # 39 # 58
      mod,level,total='Programação','1', 1363 # 3250 # 3295 #2600
    elif level==4:
      NUM_POINTS_PHASE_1=400 #500
      NUM_POINTS_PHASE_2=400# 500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  3 # 5 # 7 # 5 # 10 #4 #4 # 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 11 # 18 # 12 # 15 # 14 # 12 #10 # 8 # 7 # 9 # 12 # 11
      CUT_BRONZE =  23 # 32 # 31 # 22 # 22 # 22 #15 # 17 # 16 # 18 # 17 # 15
      CUT_HONORS =  34 # 49 # 43 # 42 # 33 #24 # 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2', 2686 # 5747 # 6471 # 5137
    elif level==5:
      NUM_POINTS_PHASE_1=300 #300
      NUM_POINTS_PHASE_2=400 #400
      NUM_POINTS_PHASE_3=400
      CUT_GOLD =  8 # 7 # 6 # 6 # 3 # 3 #1 #1 # 1 # 1 # 2 % 23
      CUT_SILVER = 16 # 19 # 17 # 14 # 11  # 13 #7 #4 # 4 # 4 # 10 # 32
      CUT_BRONZE = 23 # 41 # 27 # 34 # 27 # 29  #12 #9 # 9 # 15 # 17 # 35
      CUT_HONORS =  33 # 67 # 47 # 41 # 50 #46 #36 #18 # 15 # 25 # 22
      mod,level,total='Programação','Júnior', 477 # 1608 # 715  #982
    elif level==6:
      NUM_POINTS_PHASE_1=400 #500
      NUM_POINTS_PHASE_2=400 #500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  12 # 7 # 5 # 5 # 9 #4 #3 # 1 # 2
      CUT_SILVER = 19 # 14 # 11 # 9 # 11 #8 #4 # 5 # 6
      CUT_BRONZE = 34 # 29 # 22 # 18 # 20 #16 #11 # 14 # 12
      CUT_HONORS = 51 # 34 # 29 # 34 # 34 #27 #28 # 26 # 24
      mod,level,total='Programação','Sênior', 1142 # 1512 # 1991 # 1821
    elif level==7:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 30
      CUT_GOLD = 9 # 14 # 17 # 16 # 17
      CUT_SILVER = 22 # 33 # 36 # 44 # 50
      CUT_BRONZE = 49 # 62 # 59 # 85 # 98
      CUT_HONORS = 84 # 100 # 92 # 167 # 220
      mod,level,total='Iniciação','Júnior', 12075 # 8352 #13674 # 15345    
  elif year==2021:
    if level==1:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD =  18 #16 # 22 # 19 #25 #20 # 19 # 21 # 12 # 11
      CUT_SILVER = 46 # 44 # 59 # 66 #72 #58 # 57 # 64 # 49 # 37
      CUT_BRONZE = 73 # 79 # 135  # 125  #132 #114 # 115 # 146 # 109 # 107
      CUT_HONORS = 122 # 184 #210 #181 # 195 # 239 # 143
      mod,level,total='Iniciação','1', 16909 # 11645 #22026 #23364
    elif level==2:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD = 32 # 39 # 17 #24 #21 # 22 # 20 # 15 # 13
      CUT_SILVER = 61 # 67 # 63 # 64  #62 #66 # 55 # 67 # 40 # 37
      CUT_BRONZE =  103 # 117 # 138 # 124 #123 #134 # 127 # 122 # 101 # 104
      CUT_HONORS =  141 # 149 # 192 # 212 #192 #212 # 216 # 251 # 137
      mod,level,total='Iniciação','2', 16839 # 11935 # 21152 #24134
    elif level==3:
      NUM_POINTS_PHASE_1= 300 #400 # 300
      NUM_POINTS_PHASE_2= 400 # 400
      NUM_POINTS_PHASE_3= 400
      CUT_GOLD =  6 # 3 # 6 # 5 #2 #2 # 1 # 2 # 5 # 24
      CUT_SILVER = 17 # 9 # 11 # 7 #4 #7 # 3 # 8 # 16 # 38
      CUT_BRONZE = 28 # 20 # 20 #11 #24 # 8 # 20 # 35 # 50
      CUT_HONORS =  47 # 31 # 30 # 28 #27 #27 # 16 # 39 # 58
      mod,level,total='Programação','1', 3758 # 3250 # 3295 #2600
    elif level==4:
      NUM_POINTS_PHASE_1=400 #500
      NUM_POINTS_PHASE_2=400# 500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  5 # 7 # 5 # 10 #4 #4 # 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 18 # 12 # 15 # 14 # 12 #10 # 8 # 7 # 9 # 12 # 11
      CUT_BRONZE =  32 # 31 # 22 # 22 # 22 #15 # 17 # 16 # 18 # 17 # 15
      CUT_HONORS =  49 # 43 # 42 # 33 #24 # 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2', 7440 # 5747 # 6471 # 5137
    elif level==5:
      NUM_POINTS_PHASE_1=300 #300
      NUM_POINTS_PHASE_2=400 #400
      NUM_POINTS_PHASE_3=400
      CUT_GOLD =  7 # 6 # 6 # 3 # 3 #1 #1 # 1 # 1 # 2 % 23
      CUT_SILVER = 19 # 17 # 14 # 11  # 13 #7 #4 # 4 # 4 # 10 # 32
      CUT_BRONZE = 41 # 27 # 34 # 27 # 29  #12 #9 # 9 # 15 # 17 # 35
      CUT_HONORS =  67 # 47 # 41 # 50 #46 #36 #18 # 15 # 25 # 22
      mod,level,total='Programação','Júnior', 932 # 1608 # 715  #982
    elif level==6:
      NUM_POINTS_PHASE_1=400 #500
      NUM_POINTS_PHASE_2=400 #500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  7 # 5 # 5 # 9 #4 #3 # 1 # 2
      CUT_SILVER = 14 # 11 # 9 # 11 #8 #4 # 5 # 6
      CUT_BRONZE = 29 # 22 # 18 # 20 #16 #11 # 14 # 12
      CUT_HONORS =  34 # 29 # 34 # 34 #27 #28 # 26 # 24
      mod,level,total='Programação','Sênior', 1237 #1512 # 1991 # 1821
    elif level==7:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 30
      CUT_GOLD = 14 # 17 # 16 # 17
      CUT_SILVER = 33 # 36 # 44 # 50
      CUT_BRONZE = 62 # 59 # 85 # 98
      CUT_HONORS = 100 # 92 # 167 # 220
      mod,level,total='Iniciação','Júnior', 11812 # 8352 #13674 # 15345
  elif year==2020:
    if level==1:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD =  16 # 22 # 19 #25 #20 # 19 # 21 # 12 # 11
      CUT_SILVER = 44 # 59 # 66 #72 #58 # 57 # 64 # 49 # 37
      CUT_BRONZE = 79 # 135  # 125  #132 #114 # 115 # 146 # 109 # 107
      CUT_HONORS = 103 # 184 #210 #181 # 195 # 239 # 143
      mod,level,total='Iniciação','1', 4923 #22026 #23364
    elif level==2:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD = 39 # 17 #24 #21 # 22 # 20 # 15 # 13
      CUT_SILVER = 67 # 63 # 64  #62 #66 # 55 # 67 # 40 # 37
      CUT_BRONZE =  117 # 138 # 124 #123 #134 # 127 # 122 # 101 # 104
      CUT_HONORS =  149 # 192 # 212 #192 #212 # 216 # 251 # 137
      mod,level,total='Iniciação','2', 4715 # 21152 #24134
    elif level==3:
      NUM_POINTS_PHASE_1= 300 #400 # 300
      NUM_POINTS_PHASE_2=300 # 400
      NUM_POINTS_PHASE_3=400
      CUT_GOLD =  3 # 6 # 5 #2 #2 # 1 # 2 # 5 # 24
      CUT_SILVER = 9 # 11 # 7 #4 #7 # 3 # 8 # 16 # 38
      CUT_BRONZE = 20 # 20 #11 #24 # 8 # 20 # 35 # 50
      CUT_HONORS =  31 # 30 # 28 #27 #27 # 16 # 39 # 58
      mod,level,total='Programação','1', 601 # 3295 #2600
    elif level==4:
      NUM_POINTS_PHASE_1=300 #500
      NUM_POINTS_PHASE_2=300# 500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  7 # 5 # 10 #4 #4 # 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 12 # 15 # 14 # 12 #10 # 8 # 7 # 9 # 12 # 11
      CUT_BRONZE =  31 # 22 # 22 # 22 #15 # 17 # 16 # 18 # 17 # 15
      CUT_HONORS =  43 # 42 # 33 #24 # 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2', 1273 # 6471 # 5137
    elif level==5:
      NUM_POINTS_PHASE_1=200 #300
      NUM_POINTS_PHASE_2=300 #400
      NUM_POINTS_PHASE_3=400
      CUT_GOLD =  6 # 3 # 3 #1 #1 # 1 # 1 # 2 % 23
      CUT_SILVER = 14 # 11  # 13 #7 #4 # 4 # 4 # 10 # 32
      CUT_BRONZE = 34 # 27 # 29  #12 #9 # 9 # 15 # 17 # 35
      CUT_HONORS =  41 # 50 #46 #36 #18 # 15 # 25 # 22
      mod,level,total='Programação','Júnior', 271 # 715  #982
    elif level==6:
      NUM_POINTS_PHASE_1=300 #500
      NUM_POINTS_PHASE_2=300 #500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  5 # 5 # 9 #4 #3 # 1 # 2
      CUT_SILVER = 11 # 9 # 11 #8 #4 # 5 # 6
      CUT_BRONZE = 22 # 18 # 20 #16 #11 # 14 # 12
      CUT_HONORS =  29 # 34 # 34 #27 #28 # 26 # 24
      mod,level,total='Programação','Sênior', 869 # 1991 # 1821
    elif level==7:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 30
      CUT_GOLD = 17 # 16 # 17
      CUT_SILVER = 36 # 44 # 50
      CUT_BRONZE = 59 # 85 # 98
      CUT_HONORS = 92 # 167 # 220
      mod,level,total='Iniciação','Júnior', 3326 #13674 # 15345
  elif year==2019:
    if level==1:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 30
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD =  22 # 19 #25 #20 # 19 # 21 # 12 # 11
      CUT_SILVER = 59 # 66 #72 #58 # 57 # 64 # 49 # 37
      CUT_BRONZE = 135  # 125  #132 #114 # 115 # 146 # 109 # 107
      CUT_HONORS = 184 #210 #181 # 195 # 239 # 143
      mod,level,total='Iniciação','1', 18487 #23364
    elif level==2:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 30
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD = 17 #24 #21 # 22 # 20 # 15 # 13
      CUT_SILVER = 63 # 64  #62 #66 # 55 # 67 # 40 # 37
      CUT_BRONZE =  138 # 124 #123 #134 # 127 # 122 # 101 # 104
      CUT_HONORS =  192 # 212 #192 #212 # 216 # 251 # 137
      mod,level,total='Iniciação','2', 17481 #24134
    elif level==3:
      NUM_POINTS_PHASE_1= 300 #400 # 300
      NUM_POINTS_PHASE_2=300 # 400
      NUM_POINTS_PHASE_3=400
      CUT_GOLD =  6 # 5 #2 #2 # 1 # 2 # 5 # 24
      CUT_SILVER = 11 # 7 #4 #7 # 3 # 8 # 16 # 38
      CUT_BRONZE = 20 #11 #24 # 8 # 20 # 35 # 50
      CUT_HONORS =  30 # 28 #27 #27 # 16 # 39 # 58
      mod,level,total='Programação','1', 1481 #2600
    elif level==4:
      NUM_POINTS_PHASE_1=300 #500
      NUM_POINTS_PHASE_2=300# 500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  5 # 10 #4 #4 # 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 15 # 14 # 12 #10 # 8 # 7 # 9 # 12 # 11
      CUT_BRONZE =  22 # 22 # 22 #15 # 17 # 16 # 18 # 17 # 15
      CUT_HONORS =  42 # 33 #24 # 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2', 2933 # 5137
    elif level==5:
      NUM_POINTS_PHASE_1=200 #300
      NUM_POINTS_PHASE_2=300 #400
      NUM_POINTS_PHASE_3=300
      CUT_GOLD =  3 # 3 #1 #1 # 1 # 1 # 2 % 23
      CUT_SILVER = 11  # 13 #7 #4 # 4 # 4 # 10 # 32
      CUT_BRONZE = 27 # 29  #12 #9 # 9 # 15 # 17 # 35
      CUT_HONORS =  50 #46 #36 #18 # 15 # 25 # 22
      mod,level,total='Programação','Júnior', 470  #982
    elif level==6:
      NUM_POINTS_PHASE_1=300 #500
      NUM_POINTS_PHASE_2=300 #500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  5 # 9 #4 #3 # 1 # 2
      CUT_SILVER =  9 # 11 #8 #4 # 5 # 6
      CUT_BRONZE =  21 # 20 #16 #11 # 14 # 12
      CUT_HONORS =  34 # 34 #27 #28 # 26 # 24
      mod,level,total='Programação','Sênior', 1470 # 1821
    elif level==7:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 30
      NUM_POINTS_PHASE_3 = 30
      CUT_GOLD = 16 # 17
      CUT_SILVER = 44 # 50
      CUT_BRONZE = 85 # 98
      CUT_HONORS = 167 # 220
      mod,level,total='Iniciação','Júnior', 11836 # 15345
  elif year==2018:
    if level==1:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 30
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD =  19 #25 #20 # 19 # 21 # 12 # 11
      CUT_SILVER = 66 #72 #58 # 57 # 64 # 49 # 37
      CUT_BRONZE = 125  #132 #114 # 115 # 146 # 109 # 107
      CUT_HONORS = 204 #210 #181 # 195 # 239 # 143
      mod,level,total='Iniciação','1', 19723
    elif level==2:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 30
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD = 18 #24 #21 # 22 # 20 # 15 # 13
      CUT_SILVER = 64 #64  #62 #66 # 55 # 67 # 40 # 37
      CUT_BRONZE =  124 #123 #134 # 127 # 122 # 101 # 104
      CUT_HONORS =  212 #192 #212 # 216 # 251 # 137
      mod,level,total='Iniciação','2', 20167
    elif level==3:
      NUM_POINTS_PHASE_1= 300 #400 # 300
      NUM_POINTS_PHASE_2=300 # 400
      NUM_POINTS_PHASE_3=400
      CUT_GOLD =  5 #2 #2 # 1 # 2 # 5 # 24
      CUT_SILVER = 7 #4 #7 # 3 # 8 # 16 # 38
      CUT_BRONZE = 12 #11 #24 # 8 # 20 # 35 # 50
      CUT_HONORS =  28 #27 #27 # 16 # 39 # 58
      mod,level,total='Programação','1',1101
    elif level==4:
      NUM_POINTS_PHASE_1=300 #500
      NUM_POINTS_PHASE_2=300# 500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  10 #4 #4 # 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 14 # 12 #10 # 8 # 7 # 9 # 12 # 11
      CUT_BRONZE =  23 # 22 #15 # 17 # 16 # 18 # 17 # 15
      CUT_HONORS =  53 # 33 #24 # 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2',2133
    elif level==5:
      NUM_POINTS_PHASE_1=200 #300
      NUM_POINTS_PHASE_2=300 #400
      NUM_POINTS_PHASE_3=300
      CUT_GOLD =  3 #1 #1 # 1 # 1 # 2 % 23
      CUT_SILVER = 13 #7 #4 # 4 # 4 # 10 # 32
      CUT_BRONZE = 29  #12 #9 # 9 # 15 # 17 # 35
      CUT_HONORS =  46 #36 #18 # 15 # 25 # 22
      mod,level,total='Programação','Júnior',382
    elif level==6:
      NUM_POINTS_PHASE_1=300 #500
      NUM_POINTS_PHASE_2=300 #500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD =  9 #4 #3 # 1 # 2
      CUT_SILVER =  11 #8 #4 # 5 # 6
      CUT_BRONZE =  20 #16 #11 # 14 # 12
      CUT_HONORS =  34 #27 #28 # 26 # 24
      mod,level,total='Programação','Sênior',1433
    elif level==7:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 30
      NUM_POINTS_PHASE_3 = 30
      CUT_GOLD = 17
      CUT_SILVER = 50
      CUT_BRONZE = 98
      CUT_HONORS = 220
      mod,level,total='Iniciação','Júnior',12491
  elif year==2017:
    if level==1:
      level=1
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD = 25 #20 # 19 # 21 # 12 # 11
      CUT_SILVER = 72 #58 # 57 # 64 # 49 # 37
      CUT_BRONZE = 132 #114 # 115 # 146 # 109 # 107
      CUT_HONORS = 210 #181 # 195 # 239 # 143
      mod,level,total='Iniciação','1',19924
    elif level==2:
      NUM_POINTS_PHASE_1 = 15
      NUM_POINTS_PHASE_2 = 20
      NUM_POINTS_PHASE_3 = 40
      CUT_GOLD = 24 #21 # 22 # 20 # 15 # 13
      CUT_SILVER = 62 #66 # 55 # 67 # 40 # 37
      CUT_BRONZE = 123 #134 # 127 # 122 # 101 # 104
      CUT_HONORS = 192 #212 # 216 # 251 # 137
      mod,level,total='Iniciação','2',17394
    elif level==3:
      NUM_POINTS_PHASE_1= 200 #400 # 300
      NUM_POINTS_PHASE_2=300 # 400
      NUM_POINTS_PHASE_3=400
      CUT_GOLD = 2 #2 # 1 # 2 # 5 # 24
      CUT_SILVER = 4 #7 # 3 # 8 # 16 # 38
      CUT_BRONZE = 11 #24 # 8 # 20 # 35 # 50
      CUT_HONORS = 27 #27 # 16 # 39 # 58
      mod,level,total='Programação','1',746
    elif level==4:
      NUM_POINTS_PHASE_1=300 #500
      NUM_POINTS_PHASE_2=400# 500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD = 4 #4 # 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 12 #10 # 8 # 7 # 9 # 12 # 11
      CUT_BRONZE = 22 #15 # 17 # 16 # 18 # 17 # 15
      CUT_HONORS = 33 #24 # 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2',1684
    elif level==5:
      NUM_POINTS_PHASE_1=200 #300
      NUM_POINTS_PHASE_2=300 #400
      NUM_POINTS_PHASE_3=300
      CUT_GOLD = 1 #1 # 1 # 1 # 2 % 23
      CUT_SILVER = 7 #4 # 4 # 4 # 10 # 32
      CUT_BRONZE = 12 #9 # 9 # 15 # 17 # 35
      CUT_HONORS = 36 #18 # 15 # 25 # 22
      mod,level,total='Programação','Júnior',294
    elif level==6:
      NUM_POINTS_PHASE_1=300 #500
      NUM_POINTS_PHASE_2=400 #500
      NUM_POINTS_PHASE_3=500
      CUT_GOLD = 4 #3 # 1 # 2
      CUT_SILVER = 8 #4 # 5 # 6
      CUT_BRONZE = 16 #11 # 14 # 12
      CUT_HONORS = 27 #28 # 26 # 24
      mod,level,total='Universitária','',929

  elif year==2016:
    if level==1:
      NUM_POINTS_PHASE_1 = 25
      NUM_POINTS_PHASE_2 = 40
      CUT_GOLD = 20 # 19 # 21 # 12 # 11
      CUT_SILVER = 58 # 57 # 64 # 49 # 37
      CUT_BRONZE = 114 # 115 # 146 # 109 # 107
      CUT_HONORS = 181 # 195 # 239 # 143
      mod,level,total='Iniciação','1',15550
    elif level==2:
      NUM_POINTS_PHASE_1 = 25
      NUM_POINTS_PHASE_2 = 40
      CUT_GOLD = 21 # 22 # 20 # 15 # 13
      CUT_SILVER = 66 # 55 # 67 # 40 # 37
      CUT_BRONZE = 134 # 127 # 122 # 101 # 104
      CUT_HONORS = 212 # 216 # 251 # 137
      mod,level,total='Iniciação','2',14052
    elif level==3:
      NUM_POINTS_PHASE_1=400 # 300
      NUM_POINTS_PHASE_2=400 # 300
      CUT_GOLD = 2 # 1 # 2 # 5 # 24
      CUT_SILVER = 7 # 3 # 8 # 16 # 38
      CUT_BRONZE = 24 # 8 # 20 # 35 # 50
      CUT_HONORS = 27 # 16 # 39 # 58
      mod,level,total='Programação','1',668
    elif level==4:
      NUM_POINTS_PHASE_1=500
      NUM_POINTS_PHASE_2=500
      CUT_GOLD = 4 # 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 10 # 8 # 7 # 9 # 12 # 11
      CUT_BRONZE = 15 # 17 # 16 # 18 # 17 # 15
      CUT_HONORS = 24 # 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2',1459
    elif level==5:
      NUM_POINTS_PHASE_1=300
      NUM_POINTS_PHASE_2=400
      CUT_GOLD = 1 # 1 # 1 # 2 % 23
      CUT_SILVER = 4 # 4 # 4 # 10 # 32
      CUT_BRONZE = 9 # 9 # 15 # 17 # 35
      CUT_HONORS = 18 # 15 # 25 # 22
      mod,level,total='Programação','Júnior',216
    elif level==6:
      NUM_POINTS_PHASE_1=500
      NUM_POINTS_PHASE_2=500
      CUT_GOLD = 3 # 1 # 2 
      CUT_SILVER = 4 # 5 # 6
      CUT_BRONZE = 11 # 14 # 12
      CUT_HONORS = 28 # 26 # 24
      mod,level,total='Universitária','',772
      
  elif year==2015:
    if level==1:
      NUM_POINTS_PHASE_1 = 25
      NUM_POINTS_PHASE_2 = 40
      CUT_GOLD = 19 # 21 # 12 # 11
      CUT_SILVER = 57 # 64 # 49 # 37
      CUT_BRONZE = 115 # 146 # 109 # 107
      CUT_HONORS = 194 # 239 # 143
      mod,level,total='Iniciação','1',14084

    elif level==2:
      NUM_POINTS_PHASE_1 = 25
      NUM_POINTS_PHASE_2 = 40
      CUT_GOLD = 22 # 20 # 15 # 13
      CUT_SILVER = 55 # 67 # 40 # 37
      CUT_BRONZE = 127 # 122 # 101 # 104
      CUT_HONORS = 216 # 251 # 137
      mod,level,total='Iniciação','2',13101
      
    elif level==3:
      NUM_POINTS_PHASE_1=400 # 300
      NUM_POINTS_PHASE_2=400 # 300
      CUT_GOLD = 1 # 2 # 5 # 24
      CUT_SILVER = 3 # 8 # 16 # 38
      CUT_BRONZE = 8 # 20 # 35 # 50
      CUT_HONORS = 16 # 39 # 58
      mod,level,total='Programação','1',1604
      
    elif level==4:
      NUM_POINTS_PHASE_1=500
      NUM_POINTS_PHASE_2=500
      CUT_GOLD = 2 # 2 # 2 # 2 # 3
      CUT_SILVER = 8 # 7 # 9 # 12 # 11
      CUT_BRONZE = 17 # 16 # 18 # 17 # 15
      CUT_HONORS = 25 # 31 # 26 # 24 # 21
      mod,level,total='Programação','2',743
      
    elif level==5:
      NUM_POINTS_PHASE_1=300
      NUM_POINTS_PHASE_2=300
      CUT_GOLD = 1 # 1 # 2 % 23
      CUT_SILVER = 4 # 4 # 10 # 32
      CUT_BRONZE = 9 # 15 # 17 # 35
      CUT_HONORS = 15 # 25 # 22
      mod,level,total='Programação','Júnior',213
      
    elif level==6:
      NUM_POINTS_PHASE_1=500
      NUM_POINTS_PHASE_2=500
      CUT_GOLD = 1 # 2 
      CUT_SILVER = 5 # 6
      CUT_BRONZE = 14 # 12
      CUT_HONORS = 26 # 24
      mod,level,total='Universitária','',749
  
  elif year==2014:
    if level==1:
      NUM_POINTS_PHASE_1 = 25
      NUM_POINTS_PHASE_2 = 40
      CUT_GOLD = 21 # 12 # 11
      CUT_SILVER = 64 # 49 # 37
      CUT_BRONZE = 146 # 109 # 107
      CUT_HONORS = 239 # 143
      mod,level,total='Iniciação','1',9594
      
    elif level==2:
      NUM_POINTS_PHASE_1 = 25
      NUM_POINTS_PHASE_2 = 40
      CUT_GOLD = 20 # 15 # 13
      CUT_SILVER = 67 # 40 # 37
      CUT_BRONZE = 122 # 101 # 104
      CUT_HONORS = 251 # 137
      mod,level,total='Iniciação','2',8646
      
    elif level==3:
      NUM_POINTS_PHASE_1=400 # 300
      NUM_POINTS_PHASE_2=400 # 300
      CUT_GOLD = 2 # 5 # 24
      CUT_SILVER = 8 # 16 # 38
      CUT_BRONZE = 20 # 35 # 50
      CUT_HONORS = 39 # 58
      mod,level,total='Programação','1',1685
      
    elif level==4:
      NUM_POINTS_PHASE_1=500
      NUM_POINTS_PHASE_2=500
      CUT_GOLD = 2 # 2 # 2 # 3
      CUT_SILVER = 7 # 9 # 12 # 11
      CUT_BRONZE = 16 # 18 # 17 # 15
      CUT_HONORS = 31 # 26 # 24 # 21
      mod,level,total='Programação','2',712
      
    elif level==5:
      NUM_POINTS_PHASE_1=300
      NUM_POINTS_PHASE_2=300
      CUT_GOLD = 1 # 2 % 23
      CUT_SILVER = 4 # 10 # 32
      CUT_BRONZE = 15 # 17 # 35
      CUT_HONORS = 25 # 22
      mod,level,total='Programação','Júnior',127
      
    elif level==6:
      NUM_POINTS_PHASE_1=500
      NUM_POINTS_PHASE_2=500
      CUT_GOLD = 2 
      CUT_SILVER = 6
      CUT_BRONZE = 12
      CUT_HONORS = 24
      mod,level,total='Universitária','',406

  elif year==2013:
    if level==1:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 12 # 11
        CUT_SILVER = 49 # 37
        CUT_BRONZE = 109 # 107
        CUT_HONORS = 157 # 143
        mod,level,total='Iniciação','1',6903
    elif level==2:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 15 # 13
        CUT_SILVER = 40 # 37
        CUT_BRONZE = 101 # 104
        CUT_HONORS = 126 # 137
        mod,level,total='Iniciação','2',7493       
    elif level==3:
        NUM_POINTS_PHASE_1=400 # 300
        NUM_POINTS_PHASE_2=400 # 300
        CUT_GOLD = 5 # 24
        CUT_SILVER = 16 # 38
        CUT_BRONZE = 35 # 50
        CUT_HONORS = 58 # 58
        mod,level,total='Programação','1',1399
    elif level==4:
        NUM_POINTS_PHASE_1=400
        NUM_POINTS_PHASE_2=400
        CUT_GOLD = 2 # 2 # 3
        CUT_SILVER = 9 # 12 # 11
        CUT_BRONZE = 18 # 17 # 15
        CUT_HONORS = 26 # 24 # 21
        mod,level,total='Programação','2',885
    elif level==5:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 2 # 23
        CUT_SILVER = 10 # 32
        CUT_BRONZE = 17 # 35
        CUT_HONORS = 22 # 41
        mod,level,total='Programação','Júnior',177

  elif year==2012:
    if level==1:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 11
        CUT_SILVER = 37
        CUT_BRONZE = 107
        CUT_HONORS = 143
        mod,level,total='Iniciação','1',9808
    elif level==2:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 13
        CUT_SILVER = 37
        CUT_BRONZE = 104
        CUT_HONORS = 137
        mod,level,total='Iniciação','2',8162        
    elif level==3:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 22
        CUT_SILVER = 38
        CUT_BRONZE = 50
        CUT_HONORS = 58
        mod,level,total='Programação','1',1069
    elif level==4:
        NUM_POINTS_PHASE_1=400
        NUM_POINTS_PHASE_2=400
        CUT_GOLD = 2 
        CUT_SILVER = 12 
        CUT_BRONZE = 17 
        CUT_HONORS = 24
        mod,level,total='Programação','2',820
    elif level==5:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 23
        CUT_SILVER = 32
        CUT_BRONZE = 35
        CUT_HONORS = 41
        mod,level,total='Programação','Júnior',122

  elif year==2011:
    if level==1:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 17
        CUT_SILVER = 44
        CUT_BRONZE = 112
        CUT_HONORS = 141
        mod,level,total='Iniciação','1',9366
    elif level==2:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 13
        CUT_SILVER = 41
        CUT_BRONZE = 77
        CUT_HONORS = 123
        mod,level,total='Iniciação','2',8323        
    elif level==3:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 4
        CUT_SILVER = 10
        CUT_BRONZE = 19
        CUT_HONORS = 24
        mod,level,total='Programação','1',914
    elif level==4:
        NUM_POINTS_PHASE_1=400
        NUM_POINTS_PHASE_2=400
        CUT_GOLD = 3 
        CUT_SILVER = 11 
        CUT_BRONZE = 15 
        CUT_HONORS = 21
        mod,level,total='Programação','2',598
    elif level==5:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 4
        CUT_SILVER = 8
        CUT_BRONZE = 10
        CUT_HONORS = 13
        mod,level,total='Programação','Júnior',67

  elif year==2010:
    if level==1:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 17
        CUT_SILVER = 58
        CUT_BRONZE = 128
        CUT_HONORS = 196
        mod,level,total='Iniciação','1',12151
    elif level==2:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 20
        CUT_SILVER = 71
        CUT_BRONZE = 118
        CUT_HONORS = 179
        mod,level,total='Iniciação','2',9531       
    elif level==3:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 4
        CUT_SILVER = 11
        CUT_BRONZE = 19
        CUT_HONORS = 39
        mod,level,total='Programação','1',846
    elif level==4:
        NUM_POINTS_PHASE_1=400
        NUM_POINTS_PHASE_2=400
        CUT_GOLD = 4
        CUT_SILVER = 11 
        CUT_BRONZE = 21
        CUT_HONORS = 37
        mod,level,total='Programação','2',751
    elif level==5:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 2
        CUT_SILVER = 16
        CUT_BRONZE = 16
        CUT_HONORS = 17
        mod,level,total='Programação','Júnior',482

  elif year==2009:
    if level==1:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 19
        CUT_SILVER = 44
        CUT_BRONZE = 84
        CUT_HONORS = 152
        mod,level,total='Iniciação','1',12151
    elif level==2:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 18
        CUT_SILVER = 34
        CUT_BRONZE = 63
        CUT_HONORS = 104
        mod,level,total='Iniciação','2',9531       
    elif level==3:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 3
        CUT_SILVER = 8
        CUT_BRONZE = 20
        CUT_HONORS = 30
        mod,level,total='Programação','1',846
    elif level==4:
        NUM_POINTS_PHASE_1=400
        NUM_POINTS_PHASE_2=400
        CUT_GOLD = 2
        CUT_SILVER = 8
        CUT_BRONZE = 21
        CUT_HONORS = 40
        mod,level,total='Programação','2',751
    elif level==5:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 3
        CUT_SILVER = 6
        CUT_BRONZE = 10
        CUT_HONORS = 21
        mod,level,total='Programação','Júnior',482

  elif year==2008:
    if level==1:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 14
        CUT_SILVER = 41
        CUT_BRONZE = 91
        CUT_HONORS = 124
        mod,level,total='Iniciação','1',5990
    elif level==2:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 20
        CUT_SILVER = 42
        CUT_BRONZE = 90
        CUT_HONORS = 131
        mod,level,total='Iniciação','2',5417      
    elif level==3:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 3
        CUT_SILVER = 9
        CUT_BRONZE = 18
        CUT_HONORS = 32
        mod,level,total='Programação','1',635
    elif level==4:
        NUM_POINTS_PHASE_1=400
        NUM_POINTS_PHASE_2=400
        CUT_GOLD = 8
        CUT_SILVER = 19
        CUT_BRONZE = 37
        CUT_HONORS = 52
        mod,level,total='Programação','2',680
    elif level==5:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 1
        CUT_SILVER = 5
        CUT_BRONZE = 8
        CUT_HONORS = 13
        mod,level,total='Programação','Júnior',98

  elif year==2007:
    if level==1:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 12
        CUT_SILVER = 25
        CUT_BRONZE = 60
        CUT_HONORS = 101
        mod,level,total='Iniciação','1',3697
    elif level==2:
        NUM_POINTS_PHASE_1 = 20
        NUM_POINTS_PHASE_2 = 30
        CUT_GOLD = 1
        CUT_SILVER = 27
        CUT_BRONZE = 56
        CUT_HONORS = 95
        mod,level,total='Iniciação','2',3432      
    elif level==3:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 2
        CUT_SILVER = 4
        CUT_BRONZE = 7
        CUT_HONORS = 9
        mod,level,total='Programação','1',216
    elif level==4:
        NUM_POINTS_PHASE_1=400
        NUM_POINTS_PHASE_2=400
        CUT_GOLD = 5
        CUT_SILVER = 12
        CUT_BRONZE = 26
        CUT_HONORS = 52
        mod,level,total='Programação','2',606

  elif year==2006:
    if level==1:
        NUM_POINTS_PHASE_1 = 16
        NUM_POINTS_PHASE_2 = 28
        CUT_GOLD = 4
        CUT_SILVER = 11
        CUT_BRONZE = 26
        CUT_HONORS = 30
        mod,level,total='Iniciação','1',2751
    elif level==2:
        NUM_POINTS_PHASE_1 = 22
        NUM_POINTS_PHASE_2 = 35
        CUT_GOLD = 3
        CUT_SILVER = 8
        CUT_BRONZE = 24
        CUT_HONORS = 30
        mod,level,total='Iniciação','2',2295     
    elif level==3:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 2
        CUT_SILVER = 5
        CUT_BRONZE = 10
        CUT_HONORS = 11
        mod,level,total='Programação','1',160
    elif level==4:
        NUM_POINTS_PHASE_1=300
        NUM_POINTS_PHASE_2=300
        CUT_GOLD = 4
        CUT_SILVER = 12
        CUT_BRONZE = 22
        CUT_HONORS = 30
        mod,level,total='Programação','2',567

  elif year==2005:
    if level==1:
        NUM_POINTS_PHASE_1 = 16
        CUT_GOLD = 7
        CUT_SILVER = 22
        CUT_BRONZE = 55
        CUT_HONORS = 114
        mod,level,total='Iniciação','1',4418
    elif level==2:
        NUM_POINTS_PHASE_1 = 22
        CUT_GOLD = 1
        CUT_SILVER = 49
        CUT_BRONZE = 98
        CUT_HONORS = 171
        mod,level,total='Iniciação','2',3868     
    elif level==3:
        NUM_POINTS_PHASE_1=300
        CUT_GOLD = 1
        CUT_SILVER = 4
        CUT_BRONZE = 12
        CUT_HONORS = 22
        mod,level,total='Programação','1',290
    elif level==4:
        NUM_POINTS_PHASE_1=300
        CUT_GOLD = 20
        CUT_SILVER = 52
        CUT_BRONZE = 85
        CUT_HONORS = 127
        mod,level,total='Programação','2',1122
  else:
      print('year',year)
      usage()
  if return_all:
      return NUM_POINTS_PHASE_1,NUM_POINTS_PHASE_3,NUM_POINTS_PHASE_3,CUT_GOLD,CUT_SILVER,CUT_BRONZE,CUT_HONORS,mod,level,total
  return CUT_GOLD,CUT_SILVER,CUT_BRONZE,CUT_HONORS,mod,level,total


def medal_cuts_cf(level,year,return_all=False):
  if year==2025:
    if level==3:
      NUM_POINTS = 400
      CUT_GOLD = 2 # 3
      CUT_SILVER = 5 # 7 
      CUT_BRONZE = 12 # 12 
      CUT_HONORS = 13 # 16 
      mod,level,total='Programação','1', 243 # 197
    elif level==4:
      NUM_POINTS = 500
      CUT_GOLD = 3 # 3
      CUT_SILVER = 8 # 6
      CUT_BRONZE = 18 # 10
      CUT_HONORS = 18 # 20
      mod,level,total='Programação','2', 518 # 333
    elif level==5:
      NUM_POINTS = 400
      CUT_GOLD = 10 # 4
      CUT_SILVER = 11 # 11
      CUT_BRONZE = 14 # 21
      CUT_HONORS = 14 #40
      mod,level,total='Programação','Júnior', 119 # 102

  elif year==2024:
    if level==3:
      NUM_POINTS = 400
      CUT_GOLD = 3
      CUT_SILVER = 7 
      CUT_BRONZE = 12 
      CUT_HONORS = 16 
      mod,level,total='Programação','1', 197
    elif level==4:
      NUM_POINTS = 500
      CUT_GOLD = 3
      CUT_SILVER = 6
      CUT_BRONZE = 10
      CUT_HONORS = 20
      mod,level,total='Programação','2', 333
    elif level==5:
      NUM_POINTS = 400
      CUT_GOLD = 4
      CUT_SILVER = 11
      CUT_BRONZE = 21
      CUT_HONORS = 40
      mod,level,total='Programação','Júnior', 102

  elif year==2023:
    if level==3:
      NUM_POINTS_PHASE_1= 400
      CUT_GOLD =  1 
      CUT_SILVER =  6 
      CUT_BRONZE =  7 
      CUT_HONORS =  13 
      mod,level,total='Programação','1', 158
    elif level==4:
      NUM_POINTS_PHASE_1=400
      CUT_GOLD =  1 
      CUT_SILVER = 6
      CUT_BRONZE =  12
      CUT_HONORS =  25
      mod,level,total='Programação','2', 162
    elif level==5:
      NUM_POINTS_PHASE_1=400 
      CUT_GOLD =  2 
      CUT_SILVER = 5 
      CUT_BRONZE = 9 
      CUT_HONORS =  23 
      mod,level,total='Programação','Júnior', 91
  else:
      print('which year?',year)
      sys.exit(0)
  if return_all:
      return NUM_POINTS,CUT_GOLD,CUT_SILVER,CUT_BRONZE,CUT_HONORS,mod,level,total
  print("returning")
  return CUT_GOLD,CUT_SILVER,CUT_BRONZE,CUT_HONORS,mod,level,total

