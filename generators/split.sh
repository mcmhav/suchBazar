if [ $# -ne 1 ]; then
  echo "Need to specify file to split.";
  exit 2;
fi

awk '
  BEGIN { srand() }
  {f = rand() <= 0.9 ? "training.txt" : "validation.txt"; print > f}
' $1
