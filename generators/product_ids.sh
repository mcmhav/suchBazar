#!/bin/bash
if [ $# -eq 1 ]; then
  outputfile='product_ids.txt'
elif [ $# -eq 2 ]; then
  outputfile=$2
else
  echo "Usage: ./script.sh events.tab output.tab";
  exit 2;
fi
cat $1 | cut -f 13 | sort | uniq | sed '/NULL/d' > $outputfile
