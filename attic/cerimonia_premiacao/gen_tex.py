#!/usr/bin/env python3




def main():

        for level in ('i1','i2','pj','p1','p2'):
                print(f'{level}\n')
                with open(f"raw/{level}.txt") as f:
                        lines = f.readlines()
                lines.reverse()
                for line in lines:
                        line = line.strip()
                        order,rank,points,name,school,city,state = line.split(',')
                        print(name, r"\\")
                        print(school,r"\\")
                        print(city,r"\\")
                        print(state,r"\\")
                        print(rank,r" lugar\\")
                        print()

if __name__ == '__main__':
	main()
