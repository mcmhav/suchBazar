# Mahout files.

## Install mahout

### OSX

    brew edit mahout
    # Change to version 0.9
    brew install mahout

### Window & Linux

[Installation instructions on mahout-website](https://mahout.apache.org/developers/buildingmahout.html)

## Add this JAR to the CLASSPATH:

    export CLASSPATH=.:$CLASSPATH:/usr/local/Cellar/mahout/0.9/libexec/mahout-core-0.9-job.jar

## Run and compile:

    $ javac SampleRecommender.java && java SampleRecommender
