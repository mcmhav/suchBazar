#!/bin/bash

# Test input file with some common schemes.
INFILE=../../datasets/v2/sobazar.tab.prod

python ratings.py -i $INFILE -m naive -fx sigmoid_fixed -sr 4
python ratings.py -i $INFILE -m naive -fx sigmoid_constant -sc 30
python ratings.py -i $INFILE -m naive -fx linear

python ratings.py -i $INFILE -m recentness -fx sigmoid_fixed -sr 4
python ratings.py -i $INFILE -m recentness -fx sigmoid_constant -sc 30
python ratings.py -i $INFILE -m recentness -fx linear

python ratings.py -i $INFILE -m count -fx linear
python ratings.py -i $INFILE -m count -fx sigmoid_fixed -sr 4
python ratings.py -i $INFILE -m count -fx sigmoid_constant -sc 30
