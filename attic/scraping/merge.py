#!/usr/bin/python3

import sys


filename1 = sys.argv[1]
firstline1 = int(sys.argv[2])
filename2 = sys.argv[3]
firstline2 = int(sys.argv[4])

merged = []

lineno1 = 0
lineno2 = 0
with open(filename1,"r") as fschools1:
    with open(filename2,"r") as fschools2:
        line1 = fschools1.readline().strip()
        # first line is header
        print(line1,file=sys.stderr)
        line2 = fschools2.readline().strip()
        while line1 and line2:
            do_continue = False
            if lineno1 < firstline1:
                print(line1.strip())
                line1 = fschools1.readline().strip()
                lineno1 += 1
                do_continue = True
            if lineno2 < firstline2:
                line2 = fschools2.readline().strip()
                lineno2 += 1
                do_continue = True
            if do_continue:
                continue

            tks1 = line1.split(',') 
            tks2 = line2.split(',') 
            if tks1[2] != tks2[0]:
                print(','.join(tks1))
                line1 = fschools1.readline().strip()
                lineno1 += 1
                print('.',end='',file=sys.stderr)
                continue
            print('+',end='',file=sys.stderr)
            if tks1[6] == 'None' and tks2[1] != 'None':
                print(','.join(tks1[:6]+[tks2[1]]))
            else:
                print(','.join(tks1))

            line1 = fschools1.readline().strip()
            line2 = fschools2.readline().strip()
            if lineno1!=0 and lineno1 != 1+int(tks1[0]):
                print(file=sys.stderr)
                print(line1,file=sys.stderr)
                print(lineno1,int(tks1[0]),file=sys.stderr)
                sys.exit(0)
            lineno1 += 1
            lineno2 += 1
        while line1:
            print(line1.strip())
            lineno1 += 1
            line1 = fschools1.readline().strip()


print('\nfinal line1',lineno1,'final line2',lineno2,file=sys.stderr)
