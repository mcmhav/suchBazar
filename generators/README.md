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

## Split into a testing and validation set

    ./split.sh ratings.csv
    mv ratings.csv.90 train.csv
    mv ratings.csv.10 validation.csv
