#!/bin/bash

# Trap ctrl+c and abort all if it is entered
trap 'echo interrupted; exit' INT

# Usage function, describing the parameters to the user.
usage() { echo "Usage: ./$0 -i sobazar_input.tab"; exit 1; }

# Some parameters changable in the opts.
INFILE="-i ../datasets/v3/sobazar_events_prod_cleaned_formatted.tab"

while getopts "i:" o; do
  case "${o}" in
    i)
      INFILE="-i ${OPTARG}"
      ;;
    *)
      usage
      ;;
  esac
done

OPTS="$INFILE"
echo $OPTS

#Remove old ratings files
# rm -f generators/ratings/*;
# Generate ratings
/bin/bash generators/test.sh -b -t $OPTS;

# blend.txt -

#Todo set blend split - should be possible to run the system on single files?

# Split ratings
# ./split.sh -i ratings/blend.txt;
# Cold start split
cd evaluation;
python2.7 evaluation.py --coldstart-split ../generators/ratings/blend.txt -t -fb '1,1,1,1,0';

# make predictions
cd ../generators;
./predict.sh &
wait $!
# declare -a RA=('BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random' 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF' 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes' 'BPRSLIM' 'LeastSquareSLIM')

# Get score for the predictions
echo "Evaluating"
cd ../evaluation;
declare -a trainTestTuples=('blend_itemtrain1.txt:blend_itemtest1.txt' 'blend_itemtrain2.txt:blend_itemtest2.txt' 'blend_itemtrain3.txt:blend_itemtest3.txt' 'blend_systemtrain1.txt:blend_systemtest.txt' 'blend_systemtrain2.txt:blend_systemtest.txt' 'blend_systemtrain3.txt:blend_systemtest.txt' 'blend_usertrain1.txt:blend_usertest1.txt' 'blend_usertrain2.txt:blend_usertest2.txt' 'blend_usertrain3.txt:blend_usertest3.txt')
declare -a RA=('MostPopular')
for a in "${RA[@]}"
do
    for ttt in "${trainTestTuples[@]}"
    do
        set -- "$ttt"
        IFS=":"; declare -a Array=($*)
        echo "${Array[@]}"
        python2.7 evaluation.py -b 2 -k 20 --training-file ../generators/splits/"${Array[0]}" --test-file ../generators/splits/"${Array[1]}" --prediction-file ../generators/predictions/"${Array[0]}"-"${Array[1]}"-"$a".predictions -m
    done
done

echo 'lol, done'
# Evaluate the top K recommendations
# javac SobazarRecommender.java && java SobazarRecommender;
