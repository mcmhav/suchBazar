#!/bin/bash

# make predictions
# With MyMediaLite - installed globally

trap 'echo interrupted; exit' INT

usage() { echo "Usage: ./$0 mtodo"; exit 1; }

# Some parameters changable in the opts.
TTT=""
MYMEDIAITEM=""
MYMEDIAIRANK=""
MAHOUT=0

while getopts "t:mp" o; do
  case "${o}" in
    t)
      TTT=("${OPTARG}")
      ;;
    m)
      MAHOUT=1
      ;;
    p)
      MAHOUT=1
      ;;
    *)
      usage
      ;;
  esac
done

OPTS="$MYMEDIAITEM $MYMEDIAIRANK"

echo "Making Mahout predictions"

echo "mtodo"
