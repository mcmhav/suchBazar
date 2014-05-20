#!/bin/bash

usage() { echo "Usage: $0 [-r (randomize)] -i inputfile.txt"; exit 1; }

split() {
  awk '
    BEGIN { srand() }
    {f = rand() <= 0.9 ? "'"$2"'.9.txt" : "'"${2}"'.1.txt"; print > f}
  ' $1
}

RAND=0;
INFILE=""

while getopts "ri:" o; do
  case "${o}" in
    r)
      RAND=1
      ;;
    i)
      INFILE=${OPTARG}
      ;;
    *)
      usage
      ;;
  esac
done

if [ -z "$INFILE" ]; then
  echo "Need to specify file to split.";
  exit 2;
fi

if [ $RAND -eq 1 ]; then
  TMPFILE=/tmp/test_tmp.txt;
  perl -MList::Util -e 'print List::Util::shuffle <>' $INFILE > $TMPFILE
  split $TMPFILE $INFILE;
  rm $TMPFILE
else
  split $INFILE, $INFILE
fi
