#!/bin/bash

usage() { echo "Usage: $0 [-r (randomize)] -i inputfile.txt"; exit 1; }

split() {
  # Argument #1: Input filename. File to split.
  # Argument #2: Output directory. Absolute path to directory.
  # Argument #3: Output filename.
  ABSPATH="${2}/${3}";
  awk '
    BEGIN { srand() }
    {f = rand() <= 0.9 ? "'"${ABSPATH}"'.9.txt" : "'"${ABSPATH}"'.1.txt"; print > f}
  ' $1
}

RAND=0;
INFILE=""
OUTDIR=""

while getopts "ro:i:" o; do
  case "${o}" in
    r)
      RAND=1
      ;;
    i)
      INFILE=${OPTARG}
      ;;
    o)
      OUTDIR=${OPTARG}
      ;;
    *)
      usage
      ;;
  esac
done

if [ -z "$INFILE" ]; then
  echo "Need to specify file to split.";
  exit 1;
fi

if [ -z "$OUTDIR" ]; then
  OUTDIR=$(dirname $INFILE);
fi

if [ ! -d "$OUTDIR" ]; then
  mkdir -p $OUTDIR
fi

FILENAME=$(basename $INFILE)

if [ $RAND -eq 1 ]; then
  # Create a temporary file where we randomize.
  TMPFILE=/tmp/test_tmp.txt;
  perl -MList::Util -e 'print List::Util::shuffle <>' $INFILE > $TMPFILE

  # Split base on this file instead.
  split $TMPFILE $OUTDIR $FILENAME;
  rm $TMPFILE
else
  split $INFILE $OUTDIR $FILENAME
fi

echo "Done splitting to $OUTDIR with basename $FILENAME"
