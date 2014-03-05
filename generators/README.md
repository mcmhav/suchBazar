# Generators

## Create a ratings file

`python ratings.py proddata.tab ratings.csv`

## Split into a testing and validation set

    ./split.sh ratings.csv
    mv ratings.csv.90 train.csv
    mv ratings.csv.10 validation.csv
