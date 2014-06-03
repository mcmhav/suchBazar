# Generators

## Create a ratings file

`python ratings.py -i INPUTFILE.tab -m count -fx linear`

### Debug mode

`python ratings.py -i INPUTFILE.tab -m count -fx linear --debug`

### Different methods

There are two different counting methods:

* Counting order of events (`-m count`)
* Counting days between events (`-m recentness`)

In the former all events are sorted by timestamp and then the index of item i
is the value used in the penalization function. The penalization function may
be a sigmoid or a linear function, more below.

The second takes the days between the most recent event for user u and the
current event and uses this number of days in the penalization function.

There are two different sigmoid types:

* Fixed
* Constant

In the fixed, we provide a sigmoid ratio (`-fx sigmoid_fixed -sr 4.0`) defining
the relationship between the steepness of the graph and the shift. A higher
ratio yields a steeper graph, the steepest point is always at the mid-point of
the highest X-value.

In the constant, we provide a X-value (`-fx sigmoid_constant -sc 30`) which
defines where we want our steepest point to be. This is then used as the
steepest point for all users, independent on how many events they have.

## Blending

In order to blend two rating-files, you need a blending-configuration file, looking like:

    file1.txt 0.2
    file2.txt 0.6
    file3.txt 0.2

Or:

    file1.txt
    file2.txt
    file3.txt

The ratios need to add up to 1.0. Further the files (of course) need to exist
in the current directory. In the latter example all files are blended equally
with a ratio of ~0.33.

So you can generate a set of files by:

    ./ratings.py -i proddata.tab -m recentness -fx sigmoid_constant -sc 30
    ./ratings.py -i proddata.tab -m count -fx sigmoid_fixed -sr 4.0
    ./ratings.py -i proddata.tab -m count -fx linear

And then running the blending:

    ./blend -c files.conf -d ratings.csv

Voila.

## Using the testing script

Instead of doing all this manual labour you should use the `test.sh` script
which takes the following flags:

* `-b` if you want to blend your results
* `-p` if you want to plot your results
* `-c` if you want to clean the rating and plot folder before begining.

Edit the test-file with the methods that you want to test, and the parameters
you find useful. Then run it and check the `ratings/`-folder.

## Split into a testing and validation set

    ./split.sh ratings.csv
    mv ratings.csv.90 train.csv
    mv ratings.csv.10 validation.csv
    
## Create Binary Ratings

    cat recentness_linear.txt | awk '{$3=1;print $0}' > all_events_binary.txt
    
## Generate event data file

    python makeEventTypeFile.py -r ../generated/ratings/count_linear.txt -s sobazar.tab.prod
    
Optionally the -p flag can be added to only consider purchase events (used for purchase only evaluation)

    python makeEventTypeFile.py -r ../generated/ratings/count_linear.txt -s sobazar.tab.prod -p

    

