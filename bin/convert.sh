#!/bin/bash

FILES=`find . -name "*.html"`
for f in $FILES
do
  filename="${f%.*}"

  if file -I $f | grep -wq "iso-8859-1" || file -I $f | grep -wq "us-ascii" ; then
    echo -n "$f"

    mkdir -p converted
    cp $f ./converted
    DIR=$(dirname "$f")
    mkdir -p $DIR

    if file -I $f | grep -wq "iso-8859-1" ; then
      iconv -f ISO-8859-1 -t UTF-8 $f > "${filename}_utf8.html"
    fi
    if file -I $f | grep -wq "us-ascii" ; then
      iconv -f ascii -t UTF-8 $f > "${filename}_utf8.html"
    fi
    mv "${filename}_utf8.html" $f
    echo ": CONVERTED TO UTF-8."
  else
    echo -n "$f : UTF-8 ALREADY."
    echo ""
  fi
done
