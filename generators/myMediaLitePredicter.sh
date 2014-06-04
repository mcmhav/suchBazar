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

PREDICTIONS="$ROOT/generated/predictions"

# Some parameters changable in the opts.
TTT=""
MYMEDIAITEM=0
RECTYPE=""
RECOMMENDER=""
QUIET=0
CLEAN=0
KVAL=""

while getopts "ct:ir:qp:k:" o; do
  case "${o}" in
    c)
      CLEAN=1
      ;;
    t)
      TTT=("${OPTARG}")
      ;;
    i)
      MYMEDIAITEM=1
      ;;
    r)
      RECTYPE="${OPTARG}"
      ;;
    p)
      RECOMMENDER="${OPTARG}"
      ;;
    q)
      QUIET=1
      ;;
    k)
      KVAL="${OPTARG}"
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

if [ "$RECTYPE" !=  "" ]; then
    echo "Making MyMediaLite rating predictions with $RECOMMENDER";
    for ttt in $TTT; do
      set -- "$ttt"
      IFS=":"; declare -a Array=($*)
      echo "${Array[0]}"
      OPT=(--training-file "$ROOT/generated/splits/${Array[0]}");
      OPT+=(--test-file "$ROOT/generated/splits/${Array[1]}");
      OPT+=(--recommender $RECOMMENDER);
      OPT+=(--recommender-options $KVAL);
      # Do item predictions
      PREDFILE="$PREDICTIONS/${Array[0]}-${Array[1]}-$KVAL-$RECTYPE-$RECOMMENDER.predictions"
      OPT+=(--prediction-file "$PREDFILE");
      if [ ! -f "$PREDFILE" ] || [ $CLEAN -eq 1 ]; then
        if [ $QUIET -eq 1 ]; then
          $RECTYPE ${OPT[@]} >/dev/null &
        else
          $RECTYPE ${OPT[@]} &
        fi
      fi
    done
    wait;
    echo "Done making MyMediaLite rating predictions with $RECOMMENDER";
fi
