#!/bin/bash

file=$1
echo ${file}
sed -i "~" 's/\(url:.*\).html/\1\//' ${file}
