## How to run evaluation

### Generate cold-start splits using timestamps and filterbots</h5>

`python evaluation.py --coldstart-split ../generators/ratings/count_linear.txt -t -fb '1,1,1,1,1'`

  * `--coldstart-split` is the path of the rating file to be splitted,
  * `-t` specifies whether or not to split based on timestamps (False by default)
  * `-fb` e.g '1,1,1,1,1' specifies the filterbot settings ('0,0,0,0,0' by default)

Bot 1: Brandbot, Bot 2: AverageBot, Bot3: PopularityBot, Bot4: CriticBot, Bot5: conformityBot.

If you only want to use the brandBot and PopularityBot you do the following:

`python evaluation.py --coldstart-split ../generators/ratings/count_linear.txt -t -fb '1,0,1,0,0'`

### Evaluation of a recommender

`python evaluation.py -b 2 -k 20 --training-file ../data/user_train3.txt --test-file ../data/user_test3.txt --prediction-file ../mahout/testikus.txt`

  * `--training-file` is the path of the training file,
  * `--test-file` is the path of the test file, 
  * `--prediction-file` is the path of the prediction file,
  * `-b` the beta value for HLU
  * `-k` the value for MAP and nDCG (MAP@k, nDCG@K)
