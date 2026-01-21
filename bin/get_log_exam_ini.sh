#!/bin/sh

ID=$1


grep $1 EXAMS.log |grep "Exam started" |cut -f 1,2,5,6 -d ' ' | sed 's/Exam started/iniciou a prova/'
grep $1 EXAMS.log |cut -f 1,2,15 -d ' '|grep provaf3 | sed 's/\/prova\/provaf3\//salvou tarefa /' | sed 's/\/,//'
grep $1 EXAMS.log |grep "mark_exam begin" |cut -f 1,2,5 -d ' ' | sed 's/mark_exam/encerrou a prova/'
