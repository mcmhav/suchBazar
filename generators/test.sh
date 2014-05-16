#!/bin/bash

# Check for ctrl+c
trap 'echo interrupted; exit' INT

# Test input file with some common schemes.
INFILE=../../datasets/v2/sobazar.tab.prod

python ratings.py -i $INFILE -m naive

python ratings.py -i $INFILE -m recentness -fx sigmoid_fixed -sr 4
python ratings.py -i $INFILE -m recentness -fx sigmoid_constant -sc 30
python ratings.py -i $INFILE -m recentness -fx linear

python ratings.py -i $INFILE -m count -fx linear
python ratings.py -i $INFILE -m count -fx sigmoid_fixed -sr 4.5
python ratings.py -i $INFILE -m count -fx sigmoid_constant -sc 30
