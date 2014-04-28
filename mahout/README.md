# Mahout files.

## Install mahout

### OSX

    brew edit mahout
    # Change to version 0.9
    brew install mahout

### Window & Linux

[Installation instructions on mahout-website](https://mahout.apache.org/developers/buildingmahout.html)

## Download JAR and add to CLASSPATH:

    wget http://home.samfundet.no/~hermansc/mahout-mrlegacy-1.0-job.jar
    mv mahout-mrlegacy* jars/
    export CLASSPATH=.:$CLASSPATH:./jars/

## Run and compile:

    $ javac SobazarRecommender.java && java SobazarRecommender
