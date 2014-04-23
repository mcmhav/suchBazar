# Generators

## Create a ratings file

`python ratings.py proddata.tab ratings.csv`

### Debug mode

`python ratings.py proddata.tab ratings.csv -d`

### Different methods

Use a sigmoid function calculating based on recentness and many days it is
since an event, compared to the most recent event for a user.

`python ratings.py proddata.tab ratings.csv -m sigmoid`

A sigmoid function, much the same as the above - but instead of using number
of days, we utilize the "order" of events and the oldest events for a product
is penalized more than the newest (which is not penalized at all).

`python ratings.py proddata.tab ratings.csv -m sigmoid_count`

The two sigmoid functions are good candidates for combining in a blending function :-)

## Blending

In order to blend two rating-files, you need a blending-configuration file, looking like:

    file1.txt 0.2
    file2.txt 0.6
    file3.txt 0.2

The ratios need to add up to 1.0. Further the files (of course) need to exist in the current directory.

So you can generate a set of files by:

    ./ratings.py proddata.tab -o file1.txt -m sigmoid
    ./ratings.py proddata.tab -o file2.txt -m sigmoid_count
    ./ratings.py proddata.tab -o file3.txt -m naive 

And then running the blending:

    ./blend -c files.conf -d ratings.csv

Voila.

## Split into a testing and validation set

    ./split.sh ratings.csv
    mv ratings.csv.90 train.csv
    mv ratings.csv.10 validation.csv
