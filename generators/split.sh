if [ $# -ne 1 ]; then
  echo "Need to specify file to split.";
  exit 2;
fi

awk '
  BEGIN { srand() }
  {f = FILENAME (rand() <= 0.9 ? ".90" : ".10"); print > f}
' $1
