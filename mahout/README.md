# Mahout files.

## Install mahout

### OSX

    brew edit mahout
    # Change to version 0.9
    brew install mahout

### Window & Linux

[Installation instructions on mahout-website](https://mahout.apache.org/developers/buildingmahout.html)

## Add this JAR to the CLASSPATH:

    export CLASSPATH=.:$CLASSPATH:./jars/

## Run and compile:

    $ javac SobazarRecommender.java && java SobazarRecommender
