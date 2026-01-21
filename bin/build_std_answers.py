#!/usr/bin/env python3

import sys

def usage():
    print(f'usage: {sys.argv[0]} num_questions num_alternatives')
    sys.exit(-1)


def main():
    try:
        num_questions = int(sys.argv[1])
        num_alternatives = int(sys.argv[2])
    except:
        usage()

    if num_alternatives == 3:
        option_letters = ['A', 'B', 'C']
        answers = option_letters * 40
    elif num_alternatives == 4:
        option_letters = ['A', 'B', 'C', 'D']
        answers = option_letters * 35
    else:
        option_letters = ['A', 'B', 'C', 'D', 'E']
        answers = option_letters * 20

    content = ''
    content += '#==============\n'
    content += '# Gabarito para teste\n'
    content += '#==============\n\n'
    for i in range(num_questions):
        content += f'{i+1}. {answers[i]}\n'

    print(content)
    
if __name__=="__main__":
    main()
