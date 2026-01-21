#!/bin/bash

file=$1
echo ${file}
sed -i "~" '1{/^url:/d;}' ${file}
