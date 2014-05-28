# Trap ctrl+c
trap 'echo interrupted; exit' INT

# Exit on error
set -e

ensure_dependencies() {
  hash item_recommendation 2>/dev/null || {
    echo >&2 "I require MyMediaLite (item_recommendation and rating_prediction), but it's not installed.  Aborting.";
    exit 1;
  }
}

usage() { echo "Usage: ./$0 mtodo"; exit 1; }

# Check that MyMediaLite is installed
ensure_dependencies;

# Save the current path
CWD=$( cd "$( dirname "$0" )" && pwd );

ROOT=$( dirname "$CWD");
# Some parameters changable in the opts.
TTT=""
MYMEDIAITEM=0
MYMEDIARANK=0
RECOMMENDER=""
QUIET=0

while getopts "t:irqp:" o; do
  case "${o}" in
    t)
      TTT=("${OPTARG}")
      ;;
    i)
      MYMEDIAITEM=1
      ;;
    r)
      MYMEDIARANK=1
      ;;
    p)
      RECOMMENDER="${OPTARG}"
      ;;
    q)
      QUIET=1
      ;;
    *)
      usage
      ;;
  esac
done

STDOUT=''
if [ $QUIET -eq 1 ]; then
  STDOUT='>/dev/null 2>/dev/null';
fi

if [ "$RECOMMENDER" == "" ]; then
  echo "Need to specify recommender with -p. E.g. '-p svd'";
  exit 1
fi

if [ "$TTT" == "" ]; then
  echo "Need to specify Train-Test-Tuples with -t";
  exit 1;
fi

if [ $MYMEDIAITEM -eq 1 ] || [ $MYMEDIARANK -eq 1 ]; then
    echo "Making MyMediaLite rating predictions with $RECOMMENDER";
    for ttt in $TTT; do
      set -- "$ttt"
      IFS=":"; declare -a Array=($*)

      OPT=(--training-file "$ROOT/generated/splits/${Array[0]}");
      OPT+=(--test-file "$ROOT/generated/splits/${Array[1]}");
      OPT+=(--recommender $RECOMMENDER);

      # Do item predictions
      if [ $MYMEDIAITEM -eq 1 ]; then
        OPT+=(--prediction-file "$ROOT/generated/predictions/${Array[0]}-${Array[1]}--i-$RECOMMENDER.predictions");
        # OPT+=($STDOUT)
        # echo ${OPT[@]}
        if [ $QUIET -eq 1 ]; then
          item_recommendation ${OPT[@]} >/dev/null 2>/dev/null &
        else
          item_recommendation ${OPT[@]} $STDOUT &
        fi
      fi

      # Do rank predictions
      if [ $MYMEDIARANK -eq 1 ]; then
        OPT+=(--prediction-file "$ROOT/generated/predictions/${Array[0]}-${Array[1]}--r-$RECOMMENDER.predictions");
        if [ $QUIET -eq 1 ]; then
          rating_prediction ${OPT[@]} >/dev/null 2>/dev/null &
        else
          rating_prediction ${OPT[@]} &
        fi
      fi
    done
    wait $!
    echo "Done making MyMediaLite rating predictions with $RECOMMENDER";
fi
